from django.db import models

class Question(models.Model):
    class Block(models.TextChoices):
        E = "E", "Environmental"
        S = "S", "Social"
        G = "G", "Governance"

    class QuestionType(models.TextChoices):
        YES_NO = "yes_no", "Yes / No"
        SINGLE_CHOICE = "single_choice", "Single choice"
        SCALE = "scale", "Scale"

    internal_code = models.CharField(max_length=20, unique=True)

    text = models.TextField()
    block = models.CharField(max_length=1, choices=Block.choices)
    question_type = models.CharField(max_length=32, choices=QuestionType.choices)
    weight = models.FloatField(default=1.0)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["block", "order"]

    def __str__(self):
        return f"{self.block}{self.order}. {self.text[:50]}"


class Result(models.Model):
    company = models.ForeignKey("accounts.Company", on_delete=models.CASCADE, related_name="results")

    score_e = models.FloatField(default=0)
    score_s = models.FloatField(default=0)
    score_g = models.FloatField(default=0)
    score_total = models.FloatField(default=0)
    level = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} — {self.score_total}"

class Answer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    value = models.IntegerField()

    def __str__(self):
        return f"{self.question_id}: {self.value}"

class Recommendation(models.Model):
    class Block(models.TextChoices):
        E = "E", "Environmental"
        S = "S", "Social"
        G = "G", "Governance"

    block = models.CharField(max_length=1, choices=Block.choices)
    level = models.CharField(max_length=32)

    text_ru = models.TextField()
    text_kz = models.TextField(blank=True)
    text_en = models.TextField(blank=True)

    class Meta:
        ordering = ["block", "id"]

    def __str__(self):
        return f"{self.block} — {self.level}"