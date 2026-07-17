"""
populate_questions.py — management command для заполнения таблицы Question.

Куда положить: <django_app>/management/commands/populate_questions.py
(Django требует именно такую структуру папок: management/commands/ внутри приложения,
плюс пустой __init__.py в обеих папках management/ и commands/)

Запуск (один раз, Альнуру):
    python manage.py populate_questions

Скрипт БЕЗОПАСНО перезапускаемый (idempotent) — использует update_or_create по internal_code,
так что при повторном запуске не создаст дубликаты, а просто обновит существующие записи.

ВАЖНО — что нужно в модели Question ДО запуска этого скрипта (то, что вы обсуждали с Альнуром):
    internal_code   = models.CharField(max_length=10, unique=True)
    is_controversy  = models.BooleanField(default=False)
    severity        = models.IntegerField(null=True, blank=True)  # 1-4, только для controversy-флагов

Все обычные вопросы получают weight=1.0 (наша методология считает баллы вопросов
внутри категории равнозначными — простое среднее, без индивидуальных весов вопросов).

question_type: 25 вопросов — "scale", 5 вопросов (те, что спрашивают конкретный процент,
например "% возобновляемой энергии") — "percentage" (финальное решение: фронт рисует для них
числовое поле 0-100, а не кнопки шкалы). Это должно ТОЧНО совпадать с questions_for_db.csv
и с логикой в views_tz_compliant.py (_build_answers_from_question_map) — там процентные
вопросы обрабатываются отдельной веткой, без таблицы VALUE_TO_SCORE.
"""

from django.core.management.base import BaseCommand
from esg_config import QUESTIONS, CONTROVERSY_FLAGS, CATEGORY_NAMES

# from myapp.models import Question  # раскомментировать и поправить путь под реальное приложение

# Вопросы, которые спрашивают конкретный процент — должны получить question_type="percentage",
# а не "scale". Синхронизировано с questions_for_db.csv и views_tz_compliant.py.
PERCENTAGE_QUESTION_IDS = {"E1_2", "E3_1", "S1_2", "G1_1", "G1_3"}

# Тематический блок для каждого controversy-флага — НУЖЕН ДЛЯ ОТОБРАЖЕНИЯ В АНКЕТЕ.
# Решение команды: не делать отдельный 4-й шаг анкеты под controversy-вопросы,
# а встроить их в уже существующие 3 шага (E/S/G), присвоив каждому флагу
# наиболее подходящий по смыслу блок. is_controversy=True всё равно отдельно
# маркирует их для скоринга (calculate_controversy_cap() в esg_config.py не
# зависит от block — он смотрит только на severity сработавших флагов).
# Мұхиту на фронте нужно отрисовать эти вопросы визуально иначе (например,
# рамка/иконка ⚠️), чтобы пользователь не путал их с обычными вопросами блока.
CONTROVERSY_BLOCK_MAP = {
    "C1": "G",  # спорные вооружения — вопрос бизнес-модели/этики
    "C2": "E",  # >30% выручки от угля/нефтеносных песков
    "C3": "S",  # нарушения прав человека в цепочке поставок
    "C4": "E",  # штрафы за экологические нарушения
    "C5": "G",  # коррупция руководства
    "C6": "S",  # утечка персональных данных клиентов
    "C7": "S",  # трудовые споры/забастовки
    "C8": "E",  # отсутствие экологической политики
}


class Command(BaseCommand):
    help = "Заполняет таблицу Question всеми 30 вопросами анкеты и 8 controversy-флагами"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        # --- Обычные вопросы анкеты (30 штук) ---
        for order, q in enumerate(QUESTIONS, start=1):
            question_type = "percentage" if q["id"] in PERCENTAGE_QUESTION_IDS else "scale"
            defaults = {
                "text": str(q["text"]),
                "block": q["pillar"],  # "E" / "S" / "G"
                "question_type": question_type,
                "weight": 1.0,
                "order": order,
                "is_controversy": False,
                "severity": None,
            }
            # obj, created = Question.objects.update_or_create(
            #     internal_code=q["id"],
            #     defaults=defaults,
            # )
            # if created:
            #     created_count += 1
            # else:
            #     updated_count += 1
            self.stdout.write(f"  {q['id']:6s} | block={q['pillar']} | type={question_type:10s} | {q['text'][:50]}")

        # --- Controversy-флаги (8 штук), сразу после обычных вопросов по порядку ---
        for order, flag in enumerate(CONTROVERSY_FLAGS, start=len(QUESTIONS) + 1):
            defaults = {
                "text": str(flag["text"]),
                "block": CONTROVERSY_BLOCK_MAP.get(flag["id"]),  # тематический блок для отображения в анкете
                "question_type": "yes_no",
                "weight": None,  # у флагов вместо веса используется severity
                "order": order,
                "is_controversy": True,
                "severity": flag["severity"],
            }
            # obj, created = Question.objects.update_or_create(
            #     internal_code=flag["id"],
            #     defaults=defaults,
            # )
            # if created:
            #     created_count += 1
            # else:
            #     updated_count += 1
            self.stdout.write(f"  {flag['id']:6s} | severity={flag['severity']} | {flag['text'][:60]}")

        self.stdout.write(self.style.SUCCESS(
            f"Готово: обработано {len(QUESTIONS) + len(CONTROVERSY_FLAGS)} записей "
            f"({len(QUESTIONS)} вопросов, из них {len(PERCENTAGE_QUESTION_IDS)} типа 'percentage', "
            f"+ {len(CONTROVERSY_FLAGS)} controversy-флагов)."
        ))
