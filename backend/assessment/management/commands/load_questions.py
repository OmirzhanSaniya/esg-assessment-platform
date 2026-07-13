from django.core.management.base import BaseCommand

from assessment.models import Question
from scoring.esg_config import QUESTIONS


class Command(BaseCommand):
    help = "Load ESG questions from scoring/esg_config.py"

    def handle(self, *args, **options):

        created = 0
        updated = 0

        for q in QUESTIONS:

            obj, was_created = Question.objects.update_or_create(
                internal_code=q["id"],
                defaults={
                    "text": q["text"],
                    "block": q["pillar"],
                    "question_type": q["type"],
                    "weight": 1.0,
                    "order": int(q["id"].split("_")[-1]),
                }
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Questions loaded. Created: {created}, Updated: {updated}"
            )
        )