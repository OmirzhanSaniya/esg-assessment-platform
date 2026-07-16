import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from assessment.models import Question


PERCENTAGE_CODES = {
    "E1_2",
    "E3_1",
    "S1_2",
    "G1_1",
    "G1_3",
}


class Command(BaseCommand):
    help = "Загружает ESG-вопросы из CSV-файла в базу данных"

    @transaction.atomic
    def handle(self, *args, **options):
        assessment_directory = Path(__file__).resolve().parents[2]
        csv_path = assessment_directory / "data" / "questions.csv"

        if not csv_path.exists():
            raise CommandError(
                f"CSV-файл не найден: {csv_path}"
            )

        created_count = 0
        updated_count = 0

        with csv_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            required_columns = {
                "order",
                "internal_code",
                "block",
                "text",
                "question_type",
                "weight",
                "is_controversy",
                "severity",
            }

            if reader.fieldnames is None:
                raise CommandError("CSV-файл пустой")

            missing_columns = required_columns - set(reader.fieldnames)

            if missing_columns:
                raise CommandError(
                    "В CSV отсутствуют колонки: "
                    + ", ".join(sorted(missing_columns))
                )

            for row in reader:
                internal_code = row["internal_code"].strip()

                if not internal_code:
                    raise CommandError(
                        "Найден вопрос без internal_code"
                    )

                is_controversy = (
                    row["is_controversy"].strip().upper() == "TRUE"
                )

                block_value = row["block"].strip() or None
                severity_value = row["severity"].strip()
                weight_value = row["weight"].strip()

                question_type = row["question_type"].strip()

                if internal_code in PERCENTAGE_CODES:
                    question_type = Question.QuestionType.PERCENTAGE

                severity = (
                    int(severity_value)
                    if severity_value
                    else None
                )

                # Для controversy-вопросов вес в CSV пустой.
                # В обычном расчёте веса они не участвуют.
                weight = (
                    float(weight_value)
                    if weight_value
                    else 0.0
                )

                question, created = Question.objects.update_or_create(
                    internal_code=internal_code,
                    defaults={
                        "order": int(row["order"]),
                        "text": row["text"].strip(),
                        "block": block_value,
                        "question_type": question_type,
                        "weight": weight,
                        "is_controversy": is_controversy,
                        "severity": severity,
                    },
                )

                if created:
                    created_count += 1
                    action = "Создан"
                else:
                    updated_count += 1
                    action = "Обновлён"

                self.stdout.write(
                    f"{action}: {question.internal_code}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Создано: {created_count}, "
                f"обновлено: {updated_count}"
            )
        )