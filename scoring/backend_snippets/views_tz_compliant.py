"""
views_tz_compliant.py — ФИНАЛЬНАЯ версия, учитывающая реально согласованные с командой
изменения моделей:

    Question:  + internal_code (CharField, unique)
               + is_controversy (BooleanField)
               + severity (IntegerField, null=True)
               question_type теперь: yes_no / single_choice / scale / percentage

    Company:   industry (choices — все 14 секторов, id совпадают с esg_config.SECTORS)
               sub_industry (CharField, null=True, blank=True, без choices)

    Answer:    как в ТЗ (result_id FK, question_id FK, value INTEGER) — этого достаточно
               для регенерации PDF позже, отдельное поле "raw_answers" не нужно.

Три эндпоинта:
    POST /api/v1/submit/          -> SubmitView
    GET  /api/v1/result/{id}/     -> ResultView
    GET  /api/v1/result/{id}/pdf/ -> ResultPDFView

ВАЖНО: пути импортов моделей (`from .models import ...`) нужно поправить под
реальную структуру Django-приложения — здесь placeholder `myapp.models`.
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from esg_config import calculate_esg_score, generate_roadmap_from_answers, get_sector_name, get_subindustry_name
from api_adapter import adapt_result_to_tz_format, get_tz_level
from report_generator import generate_pdf_report, send_report_email

# from myapp.models import Company, Question, Answer, Result  # поправить под реальный путь


# ============================================================
# Общая логика конвертации ответов (используется в SubmitView
# и при регенерации PDF/результата из уже сохранённых Answer)
# ============================================================

VALUE_TO_SCORE = {0: 0, 1: 25, 2: 75, 3: 100}  # Никогда/Иногда/Регулярно/Всегда -> шкала методологии


def _build_answers_from_question_map(raw_answers: list, question_map: dict) -> tuple:
    """
    raw_answers: [{"question_id": 1, "value": 2}, ...]
    question_map: {question_id (int): Question instance}, уже загруженный из БД одним запросом
                  (см. вызовы ниже — используем Question.objects.filter(id__in=...) вместо
                  запроса в цикле, чтобы не плодить N+1 запросов к базе).

    Возвращает (our_answers, our_controversy) — ровно то, что ждёт esg_config.calculate_esg_score().
    """
    our_answers = {}
    our_controversy = {}

    for item in raw_answers:
        question = question_map.get(item["question_id"])
        if question is None:
            continue  # вопрос с таким id не найден — пропускаем (можно и вернуть 400, если нужна строгая валидация)

        code = question.internal_code
        value = item["value"]

        if question.is_controversy:
            # Controversy-флаги — обычный yes/no с фронта: 1 = "да" (флаг сработал), 0 = "нет"
            our_controversy[code] = bool(value)
        elif question.question_type == "percentage":
            # Процентные вопросы — фронт уже присылает готовый процент (0-100), без конвертации
            our_answers[code] = float(value)
        else:
            # Обычные scale/yes_no/single_choice вопросы — конвертируем 0-3 в шкалу методологии
            our_answers[code] = VALUE_TO_SCORE.get(value, 0)

    return our_answers, our_controversy


def _recompute_from_stored_answers(result_obj) -> tuple:
    """
    Восстанавливает (result, roadmap) по уже сохранённому result_obj, читая связанные
    Answer-записи из БД. Используется в ResultView и ResultPDFView — чтобы не хранить
    ничего специального сверх того, что и так требует схема ТЗ.

    ВАЖНО (i18n): как и в SubmitView — язык должен быть активирован ДО вызова
    calculate_esg_score() ниже. В обычном request-cycle это уже сделано LocaleMiddleware
    к моменту, когда выполнение доходит до этой функции. Но если код вызывается вне
    запроса (Celery, management-команда, скрипт) — вызови translation.activate(lang)
    перед _recompute_from_stored_answers(), иначе получишь смесь языков.
    """
    # answer_qs = Answer.objects.filter(result=result_obj).select_related("question")
    # question_map = {a.question.id: a.question for a in answer_qs}
    # raw_answers = [{"question_id": a.question.id, "value": a.value} for a in answer_qs]
    # our_answers, our_controversy = _build_answers_from_question_map(raw_answers, question_map)

    # company = result_obj.company
    # result = calculate_esg_score(
    #     answers=our_answers,
    #     controversy_answers=our_controversy,
    #     sector_id=company.industry,        # id совпадают напрямую, без маппинга
    #     sub_industry_id=company.sub_industry or None,
    # )
    # roadmap = generate_roadmap_from_answers(result, our_controversy)
    # return result, roadmap
    raise NotImplementedError("Раскомментировать после подключения реальных моделей Answer/Result")


# ============================================================
# 1. POST /api/v1/submit/
# ============================================================

class SubmitView(APIView):
    """
    Принимает ответы анкеты, считает скор, сохраняет результат + ответы в БД,
    автоматически отправляет PDF на email компании (из аккаунта, не из body).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user.company

        raw_answers = request.data.get("answers", [])
        if not raw_answers:
            return Response({"error": "Поле 'answers' обязательно"}, status=status.HTTP_400_BAD_REQUEST)

        # Один запрос к БД за всеми нужными вопросами, а не N+1 в цикле
        # question_ids = [item["question_id"] for item in raw_answers]
        # question_map = {q.id: q for q in Question.objects.filter(id__in=question_ids)}
        question_map = {}  # заменить на строку выше после подключения модели Question

        our_answers, our_controversy = _build_answers_from_question_map(raw_answers, question_map)

        # ВАЖНО (порядок вызовов для i18n): язык должен быть активирован ДО вызова
        # calculate_esg_score()/generate_roadmap_from_answers() — переводимые строки
        # (tier, category_name, текст рекомендаций) "запекаются" в str() в момент
        # выполнения этих функций, а не в момент рендера шаблона/сериализации ответа.
        # В обычном Django request-cycle это работает само собой: LocaleMiddleware
        # активирует язык по Accept-Language ДО того, как выполнение дойдёт до этой
        # строки кода. НО если PDF/email будут генерироваться вне request-cycle
        # (например, в Celery-таске для отложенной отправки) — там нужно вызвать
        # translation.activate(company.language) вручную ПЕРЕД этим блоком, иначе
        # получится смесь языков (статичные части шаблона переведутся, а динамические
        # данные — нет, останутся на языке, который был активен на момент расчёта).
        result = calculate_esg_score(
            answers=our_answers,
            controversy_answers=our_controversy,
            sector_id=company.industry,           # id совпадают с esg_config.SECTORS напрямую
            sub_industry_id=company.sub_industry or None,
        )
        roadmap = generate_roadmap_from_answers(result, our_controversy)

        # --- Сохранение результата (модель Result по ТЗ, раздел 4.5) ---
        # result_obj = Result.objects.create(
        #     company=company,
        #     score_e=result["pillar_scores"]["E"],
        #     score_s=result["pillar_scores"]["S"],
        #     score_g=result["pillar_scores"]["G"],
        #     score_total=result["esg_final"],
        #     level=get_tz_level(result["esg_final"]),
        # )
        # --- Сохранение каждого отдельного ответа (модель Answer по ТЗ, раздел 4.4) ---
        # Answer.objects.bulk_create([
        #     Answer(result=result_obj, question_id=item["question_id"], value=item["value"])
        #     for item in raw_answers
        # ])
        result_id = None  # заменить на result_obj.id после подключения моделей

        # --- Email отправляется автоматически ---
        try:
            pdf_bytes = generate_pdf_report(
                result=result,
                roadmap=roadmap,
                company_name=company.name,
                sector_name=get_sector_name(company.industry),
                sub_industry_name=get_subindustry_name(company.industry, company.sub_industry),
            )
            send_report_email(
                pdf_bytes=pdf_bytes,
                recipient_email=request.user.email,
                company_name=company.name,
                tier_label=result["tier"],
                esg_final=result["esg_final"],
            )
        except Exception as e:
            print(f"Не удалось отправить email: {e}")  # заменить на logging в проде

        return Response({"result_id": result_id}, status=status.HTTP_201_CREATED)


# ============================================================
# 2. GET /api/v1/result/{id}/
# ============================================================

class ResultView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        # result_obj = get_object_or_404(Result, id=id, company=request.user.company)
        # result, roadmap = _recompute_from_stored_answers(result_obj)
        # tz_result = adapt_result_to_tz_format(result, roadmap, company_name=result_obj.company.name)
        # return Response(tz_result)
        raise NotImplementedError("Подключить после того, как модели Result/Answer будут готовы")


# ============================================================
# 3. GET /api/v1/result/{id}/pdf/
# ============================================================

class ResultPDFView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        # result_obj = get_object_or_404(Result, id=id, company=request.user.company)
        # result, roadmap = _recompute_from_stored_answers(result_obj)
        # pdf_bytes = generate_pdf_report(
        #     result=result,
        #     roadmap=roadmap,
        #     company_name=result_obj.company.name,
        #     sector_name=get_sector_name(result_obj.company.industry),
        #     sub_industry_name=get_subindustry_name(result_obj.company.industry, result_obj.company.sub_industry),
        # )
        # response = HttpResponse(pdf_bytes, content_type="application/pdf")
        # response["Content-Disposition"] = f'attachment; filename="ESG_report_{id}.pdf"'
        # return response
        raise NotImplementedError("Подключить после того, как модели Result/Answer будут готовы")
