from django.db import models


class Company(models.Model):
    INDUSTRY_CHOICES = [
        ("IT", "IT"),
        ("INDUSTRY", "Промышленность"),
        ("EDUCATION", "Образование"),
        ("MINING", "Добыча"),
        ("OTHER", "Другое"),
    ]

    name = models.CharField(max_length=255)
    industry = models.CharField(
        max_length=100,
        choices=INDUSTRY_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    BLOCK_CHOICES = [
        ("E", "Environmental"),
        ("S", "Social"),
        ("G", "Governance"),
    ]

    TYPE_CHOICES = [
        ("yes_no", "Да/Нет"),
        ("single_choice", "Один вариант"),
        ("scale", "Шкала"),
    ]

    text = models.TextField()

    block = models.CharField(
        max_length=1,
        choices=BLOCK_CHOICES
    )

    question_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    weight = models.FloatField(default=1.0)

    order = models.IntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    value = models.IntegerField()

    def __str__(self):
        return f"{self.company} - {self.question}"


class Result(models.Model):
    LEVEL_CHOICES = [
        ("BEGINNER", "Начальный"),
        ("DEVELOPING", "Развивающийся"),
        ("ADVANCED", "Продвинутый"),
        ("LEADER", "Лидер"),
    ]

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
        max_length=30,
        choices=LEVEL_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class Recommendation(models.Model):
    BLOCK_CHOICES = [
        ("E", "Environmental"),
        ("S", "Social"),
        ("G", "Governance"),
    ]

    block = models.CharField(
        max_length=1,
        choices=BLOCK_CHOICES
    )

    level = models.CharField(
        max_length=30
    )

    text = models.TextField()

    def __str__(self):
        return f"{self.block} - {self.level}"