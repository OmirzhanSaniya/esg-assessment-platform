"""
conftest.py — pytest подхватывает этот файл автоматически.

esg_config.py теперь использует django.utils.translation (для i18n),
поэтому перед импортом модуля нужно, чтобы Django settings были сконфигурированы —
иначе тесты падают с ImproperlyConfigured.

Если тесты запускаются внутри реального Django-проекта (через `pytest-django`
или `python manage.py test`) — этот файл не нужен, Django уже настроен самим проектом.
Он нужен только для запуска тестов ИЗОЛИРОВАННО, без полного Django-проекта вокруг.
"""

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        USE_I18N=True,
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
    )
    django.setup()
