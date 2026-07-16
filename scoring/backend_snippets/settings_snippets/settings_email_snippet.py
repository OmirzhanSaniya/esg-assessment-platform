# settings_email_snippet.py
# Добавь это в settings.py своего Django-проекта.
# Значения — брать из переменных окружения (.env), НИКОГДА не хранить пароль в коде напрямую.
#
# Использует python-decouple (уже есть в requirements.txt проекта) — специально
# не добавляли python-dotenv поверх, чтобы не плодить два разных способа читать
# .env в одном проекте.

from decouple import config

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# --- Пример для Gmail ---
# 1. Включи двухфакторную аутентификацию в Google-аккаунте.
# 2. Создай "пароль приложения" (App Password) в настройках безопасности — обычный пароль от почты не сработает.
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")          # например: yourproject@gmail.com
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")  # App Password, НЕ обычный пароль
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- Пример для Яндекс.Почты (закомментировано, раскомментируй если используешь Яндекс вместо Gmail) ---
# EMAIL_HOST = "smtp.yandex.ru"
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True   # у Яндекса обычно SSL на 465, а не TLS на 587
# EMAIL_USE_TLS = False
# EMAIL_HOST_USER = config("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")  # тоже нужен пароль приложения, не основной
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# --- .env файл (не коммитить в git, добавить в .gitignore!) ---
# EMAIL_HOST_USER=yourproject@gmail.com
# EMAIL_HOST_PASSWORD=xxxxxxxxxxxxxxxx   # App Password из Google/Yandex, 16 символов без пробелов
#
# decouple сам найдёт и прочитает .env из корня проекта — никакого дополнительного
# load_dotenv() вызывать не нужно, это не требуется в отличие от python-dotenv.


# --- Быстрая проверка, что отправка работает (запусти в Django shell: python manage.py shell) ---
# from django.core.mail import send_mail
# send_mail(
#     "Тестовое письмо",
#     "Если это письмо пришло — SMTP настроен верно.",
#     None,  # использует DEFAULT_FROM_EMAIL
#     ["куда-то-твой-email@example.com"],
# )