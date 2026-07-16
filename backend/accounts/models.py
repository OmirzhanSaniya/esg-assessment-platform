from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
    
    
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

    objects = CustomUserManager()


class Company(models.Model):

    INDUSTRY_CHOICES = (
        ("energy", "Энергетика (нефть, газ, уголь)"),
        ("mining", "Добывающая промышленность и металлургия"),
        ("utilities", "Коммунальные услуги (Utilities)"),
        ("manufacturing", "Промышленное производство"),
        ("construction", "Строительство и недвижимость"),
        ("transport", "Транспорт и логистика"),
        ("financial", "Финансовые услуги"),
        ("tech", "Технологии и ПО"),
        ("telecom", "Телекоммуникации и медиа"),
        ("retail", "Ритейл и товары народного потребления"),
        ("healthcare", "Здравоохранение и фармацевтика"),
        ("agriculture", "Сельское хозяйство и производство продуктов питания"),
        ("services", "Профессиональные услуги / образование / консалтинг"),
        ("other", "Прочее"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    industry = models.CharField(
        max_length=30,
        choices=INDUSTRY_CHOICES
    )

    sub_industry = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name