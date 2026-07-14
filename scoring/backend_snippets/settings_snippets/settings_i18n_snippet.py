# settings_i18n_snippet.py
# Добавь это в settings.py своего Django-проекта, плюс положи папку locale/
# (с уже готовыми en/ и kk/ переводами) в корень проекта — рядом с manage.py,
# либо укажи в LOCALE_PATHS путь туда, где реально лежит эта папка.

import os
from django.utils.translation import gettext_lazy as _

# --- Включаем i18n ---
USE_I18N = True
USE_L10N = True  # форматирование чисел/дат под локаль (опционально, но обычно нужно)

# --- Язык по умолчанию (когда не указан явно и не определён по Accept-Language) ---
LANGUAGE_CODE = "ru"

# --- Доступные языки сайта ---
LANGUAGES = [
    ("ru", _("Русский")),
    ("kk", _("Қазақша")),
    ("en", _("English")),
]

# --- Где искать .po/.mo файлы с переводами ---
# Путь ниже предполагает, что папка locale/ лежит в корне Django-проекта
# (там же, где manage.py). Поправь путь, если структура другая.
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),  # BASE_DIR уже должен быть определён в settings.py
]

# --- ОБЯЗАТЕЛЬНО: LocaleMiddleware должен стоять после SessionMiddleware
#     и до CommonMiddleware — иначе Django не будет автоматически определять
#     язык по Accept-Language заголовку / сессии / cookie ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # <-- добавить именно сюда, после Session
    "django.middleware.common.CommonMiddleware",
    # ...остальные твои middleware
]


# ============================================================
# Как переключать язык — 3 стандартных способа Django, выбери подходящий:
# ============================================================

# СПОСОБ 1 (проще всего для API/SPA-фронтенда, как у вас с React):
# Фронтенд просто передаёт заголовок Accept-Language при каждом запросе —
# LocaleMiddleware сам разберёт его и активирует нужный язык на время запроса.
# Ничего дополнительно писать в Django не нужно, работает "из коробки".
#
# fetch("/api/v1/questions/", {
#     headers: { "Accept-Language": "kk" }
# })


# СПОСОБ 2 (язык как часть URL, например /kk/api/v1/questions/):
# Требует i18n_patterns в urls.py:
#
# from django.conf.urls.i18n import i18n_patterns
# urlpatterns = i18n_patterns(
#     path('api/v1/', include('myapp.urls')),
# )


# СПОСОБ 3 (явный параметр в запросе, если удобнее фронту):
# Можно сделать свой небольшой middleware/декоратор, который читает
# ?lang=kk или заголовок X-Language и вызывает:
#
# from django.utils import translation
# translation.activate(request_lang)


# ============================================================
# Команды для сборки/обновления переводов (если позже добавите новые строки)
# ============================================================
# python manage.py makemessages -l kk -l en   # найдёт новые _("...") строки в коде
# python manage.py compilemessages            # скомпилирует .po -> .mo (нужен gettext в системе)
#
# ВАЖНО: команды выше используют СТАНДАРТНЫЙ django-admin gettext-пайплайн.
# Если просто добавите новые строки в esg_config.py, оборачивая их в _(...),
# makemessages сам найдёт их и добавит в .po файлы — переводы для новых строк
# нужно будет дописать вручную (Django не переводит сам, только находит).
