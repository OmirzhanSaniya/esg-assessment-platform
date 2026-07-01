from django.db import models
from accounts.models import Company

class Question(models.Model):

    BLOCKS = (
        ("E", "Environmental"),
        ("S", "Social"),
        ("G", "Governance"),
    )

    TYPES = (
        ("yes_no", "Yes/No"),
        ("single_choice", "Single Choice"),
        ("scale", "Scale"),
    )

    text = models.TextField()

    block = models.CharField(
        max_length=1,
        choices=BLOCKS
    )

    question_type = models.CharField(
        max_length=20,
        choices=TYPES
    )

    weight = models.FloatField(default=1)

    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.block} - {self.order}"


class Result(models.Model):

    LEVELS = (
        ("beginner", "Beginner"),
        ("developing", "Developing"),
        ("advanced", "Advanced"),
        ("leader", "Leader"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="results"
    )

    score_e = models.FloatField()

    score_s = models.FloatField()

    score_g = models.FloatField()

    score_total = models.FloatField()

    level = models.CharField(
        max_length=20,
        choices=LEVELS
    )

    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):

    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    value = models.PositiveSmallIntegerField()


class Recommendation(models.Model):

    BLOCKS = (
        ("E", "Environmental"),
        ("S", "Social"),
        ("G", "Governance"),
    )

    LEVELS = (
        ("beginner", "Beginner"),
        ("developing", "Developing"),
        ("advanced", "Advanced"),
        ("leader", "Leader"),
    )

    block = models.CharField(
        max_length=1,
        choices=BLOCKS
    )

    level = models.CharField(
        max_length=20,
        choices=LEVELS
    )

    text_ru = models.TextField()

    text_kz = models.TextField()

    text_en = models.TextField()