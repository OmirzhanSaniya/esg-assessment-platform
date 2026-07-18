import logging

from django.db import transaction
from django.db.models import Avg, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Company, User
from scoring.api_adapter import adapt_result_to_tz_format
from scoring.esg_config import (
    calculate_esg_score,
    generate_roadmap_from_answers,
    get_sector_name,
    get_subindustry_name,
)
from scoring.report_generator import generate_pdf_report, send_report_email

from .models import Answer, Question, Result
from .serializers import (
    AdminStatsSerializer,
    QuestionSerializer,
    RatingSerializer,
    SubmitAssessmentSerializer,
)

logger = logging.getLogger(__name__)

# Значения кнопок фронта 0..3 переводятся в шкалу методологии.
VALUE_TO_SCORE = {0: 0, 1: 25, 2: 75, 3: 100}


class IsESGAdmin(BasePermission):
    """Поддерживает и Django is_staff, и вашу бизнес-роль role='admin'."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                getattr(user, "is_staff", False)
                or getattr(user, "role", None) == "admin"
            )
        )


def _build_answers_from_question_map(raw_answers, question_map):
    """Проверяет raw-значения и преобразует их к формату esg_config.py."""
    scoring_answers = {}
    controversy_answers = {}

    for item in raw_answers:
        question_id = item["question_id"]
        value = item["value"]
        question = question_map.get(question_id)

        if question is None:
            raise ValidationError(
                {"answers": f"Вопрос с id={question_id} не существует."}
            )

        if question.is_controversy:
            if value not in (0, 1):
                raise ValidationError(
                    {
                        "answers": (
                            f"Для controversy-вопроса {question.internal_code} "
                            "значение должно быть 0 или 1."
                        )
                    }
                )
            controversy_answers[question.internal_code] = bool(value)
            continue

        if question.question_type == Question.QuestionType.PERCENTAGE:
            if not 0 <= value <= 100:
                raise ValidationError(
                    {
                        "answers": (
                            f"Для процентного вопроса {question.internal_code} "
                            "значение должно быть от 0 до 100."
                        )
                    }
                )
            scoring_answers[question.internal_code] = float(value)
            continue

        if question.question_type == Question.QuestionType.YES_NO:
            if value not in (0, 1):
                raise ValidationError(
                    {
                        "answers": (
                            f"Для yes/no-вопроса {question.internal_code} "
                            "значение должно быть 0 или 1."
                        )
                    }
                )
        elif value not in VALUE_TO_SCORE:
            raise ValidationError(
                {
                    "answers": (
                        f"Для вопроса {question.internal_code} "
                        "значение должно быть 0, 1, 2 или 3."
                    )
                }
            )

        scoring_answers[question.internal_code] = VALUE_TO_SCORE[value]

    return scoring_answers, controversy_answers


def _recompute_from_stored_answers(result_obj):
    """
    Восстанавливает подробный результат и roadmap из сохранённых Answer.

    LocaleMiddleware уже должен активировать язык до вызова этой функции.
    Для Celery/management command сначала вызывай translation.activate(lang).
    """
    stored_answers = list(
        result_obj.answers.select_related("question").all()
    )
    question_map = {
        answer.question_id: answer.question
        for answer in stored_answers
    }
    raw_answers = [
        {
            "question_id": answer.question_id,
            "value": answer.value,
        }
        for answer in stored_answers
    ]

    scoring_answers, controversy_answers = _build_answers_from_question_map(
        raw_answers,
        question_map,
    )

    company = result_obj.company
    sub_industry = getattr(company, "sub_industry", None) or None

    result = calculate_esg_score(
        answers=scoring_answers,
        controversy_answers=controversy_answers,
        sector_id=company.industry,
        sub_industry_id=sub_industry,
    )
    roadmap = generate_roadmap_from_answers(
        result,
        controversy_answers,
    )
    return result, roadmap


class QuestionListView(APIView):
    """GET /api/v1/questions/ — вопросы, сгруппированные по E/S/G."""

    def get(self, request):
        questions = Question.objects.all().order_by("block", "order")
        serializer = QuestionSerializer(questions, many=True)

        grouped = {"E": [], "S": [], "G": []}
        for question in serializer.data:
            block = question["block"]
            if block in grouped:
                grouped[block].append(question)

        return Response(grouped)


class SubmitView(APIView):
    """POST /api/v1/submit/ — расчёт, сохранение Answer/Result, PDF на email."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubmitAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data["answers"]

        company = getattr(request.user, "company", None)
        if company is None:
            return Response(
                {"detail": "Для пользователя не создан профиль компании."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question_ids = [item["question_id"] for item in raw_answers]
        question_map = {
            question.id: question
            for question in Question.objects.filter(id__in=question_ids)
        }

        missing_ids = sorted(set(question_ids) - set(question_map))
        if missing_ids:
            raise ValidationError(
                {"answers": f"Вопросы не найдены: {missing_ids}."}
            )

        scoring_answers, controversy_answers = _build_answers_from_question_map(
            raw_answers,
            question_map,
        )

        # LocaleMiddleware активировал язык ДО этого места по Accept-Language.
        sub_industry = getattr(company, "sub_industry", None) or None
        result = calculate_esg_score(
            answers=scoring_answers,
            controversy_answers=controversy_answers,
            sector_id=company.industry,
            sub_industry_id=sub_industry,
        )
        roadmap = generate_roadmap_from_answers(
            result,
            controversy_answers,
        )

        with transaction.atomic():
            result_obj = Result.objects.create(
                company=company,
                score_e=result["pillar_scores"]["E"],
                score_s=result["pillar_scores"]["S"],
                score_g=result["pillar_scores"]["G"],
                score_total=result["esg_final"],
                # Везде используем одну и ту же 5-тирную систему esg_config.py.
                level=result["tier"],
            )

            Answer.objects.bulk_create(
                [
                    Answer(
                        result=result_obj,
                        question=question_map[item["question_id"]],
                        value=item["value"],
                    )
                    for item in raw_answers
                ]
            )

        # Ошибка SMTP не должна откатывать уже сохранённую оценку.
        try:
            pdf_bytes = generate_pdf_report(
                result=result,
                roadmap=roadmap,
                company_name=company.name,
                sector_name=get_sector_name(company.industry),
                sub_industry_name=get_subindustry_name(
                    company.industry,
                    sub_industry,
                ),
            )
            send_report_email(
                pdf_bytes=pdf_bytes,
                recipient_email=request.user.email,
                company_name=company.name,
                tier_label=result["tier"],
                esg_final=result["esg_final"],
            )
        except Exception:
            logger.exception(
                "Не удалось сформировать или отправить ESG PDF для result_id=%s",
                result_obj.id,
            )

        return Response(
            {"result_id": result_obj.id},
            status=status.HTTP_201_CREATED,
        )


class ResultView(APIView):
    """GET /api/v1/result/{id}/ — только результат текущей компании."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        result_obj = get_object_or_404(
            Result.objects.select_related("company").prefetch_related(
                "answers__question"
            ),
            pk=pk,
            company=request.user.company,
        )
        result, roadmap = _recompute_from_stored_answers(result_obj)
        payload = adapt_result_to_tz_format(
            result,
            roadmap,
            company_name=result_obj.company.name,
        )
        payload["result_id"] = result_obj.id
        payload["created_at"] = result_obj.created_at.isoformat()
        return Response(payload)


class ResultPDFView(APIView):
    """GET /api/v1/result/{id}/pdf/ — PDF из истории текущей компании."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        result_obj = get_object_or_404(
            Result.objects.select_related("company").prefetch_related(
                "answers__question"
            ),
            pk=pk,
            company=request.user.company,
        )
        result, roadmap = _recompute_from_stored_answers(result_obj)
        company = result_obj.company
        sub_industry = getattr(company, "sub_industry", None) or None

        pdf_bytes = generate_pdf_report(
            result=result,
            roadmap=roadmap,
            company_name=company.name,
            sector_name=get_sector_name(company.industry),
            sub_industry_name=get_subindustry_name(
                company.industry,
                sub_industry,
            ),
        )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="ESG_report_{pk}.pdf"'
        )
        return response


class AdminStatsView(APIView):
    permission_classes = [IsESGAdmin]

    def get(self, request):
        average = Result.objects.aggregate(avg=Avg("score_total"))["avg"] or 0
        data = {
            "users": User.objects.count(),
            "companies": Company.objects.count(),
            "assessments": Result.objects.count(),
            "average_score": round(average, 2),
        }
        return Response(AdminStatsSerializer(data).data)


class RatingListView(ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        # Берём только последнюю оценку каждой компании, затем сортируем по баллу.
        latest_result_id = (
            Result.objects.filter(company_id=OuterRef("company_id"))
            .order_by("-created_at")
            .values("id")[:1]
        )
        queryset = (
            Result.objects.select_related("company")
            .filter(id=Subquery(latest_result_id))
        )

        industry = self.request.query_params.get("industry")
        if industry:
            queryset = queryset.filter(company__industry=industry)

        return queryset.order_by("-score_total", "company__name")
