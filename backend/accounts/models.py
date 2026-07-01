from django.contrib.auth.models import AbstractUser
from django.db import models

from django.conf import settings


class User(AbstractUser):
    username = None

    ROLE_CHOICES = (
        ("company", "Company"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Company(models.Model):

    INDUSTRY_CHOICES = (
        ("IT", "IT"),
        ("INDUSTRY", "Industry"),
        ("EDUCATION", "Education"),
        ("MINING", "Mining"),
        ("OTHER", "Other"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    industry = models.CharField(
        max_length=20,
        choices=INDUSTRY_CHOICES
    )

    def __str__(self):
        return self.name    