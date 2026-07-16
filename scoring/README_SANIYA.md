# Сания — файлы для GitHub (актуальные версии, проверено)

Все файлы здесь — последние проверенные версии (прогнаны тесты, скомпилированы
переводы, отрендерен PDF на 3 языках). Ниже — куда что класть в реальном
Django-проекте команды.

## scoring/  — ядро методологии, не зависит от структуры Django-приложения
- `esg_config.py` — вся методология: секторы, вопросы, скоринг, роадмап,
  controversy overlay, i18n (gettext_lazy), `get_sector_name()` / `get_subindustry_name()`.
- `test_esg_config.py` — 39 pytest-тестов.
- `conftest.py` — нужен ТОЛЬКО если тесты гоняются отдельно от Django-проекта
  (см. комментарий внутри файла). Если тесты идут через `pytest-django` внутри
  реального проекта — этот файл не нужен, Django уже настроен самим проектом.

Положить: `scoring/` в корень репозитория (как в структуре ТЗ, раздел 8), либо
эквивалентную папку внутри `backend/`, куда договорились с командой.

Проверка: `cd scoring && python -m pytest` → 39 passed.

## backend_snippets/  — код для подключения к реальным моделям Django
- `views_tz_compliant.py` → положить как view для `POST /api/v1/submit/`,
  `GET /api/v1/result/{id}/`, `GET /api/v1/result/{id}/pdf/`. Внутри — заглушки
  с `# from myapp.models import ...` — их должен раскомментировать и поправить
  под реальные модели Альнур (он владеет Question/Answer/Result).
- `api_adapter.py` → адаптер результата под формат ответа из ТЗ (раздел 5.5).
- `report_generator.py` → генерация PDF (WeasyPrint) + отправка email (SMTP).
- `management/commands/populate_questions.py` → положить именно в
  `<django_app>/management/commands/populate_questions.py` (с пустыми
  `__init__.py` в обеих папках). Заполняет таблицу Question всеми 30 вопросами
  + 8 controversy-флагами, включая правильные `question_type` (5 вопросов —
  `percentage`, остальные — `scale`).
- `templates/reports/esg_report_template.html` → положить в папку шаблонов
  Django-приложения (`<app>/templates/reports/esg_report_template.html`).
  Уже полностью на i18n (`{% load i18n %}` / `{% trans %}` / `{% blocktrans %}`).
- `settings_snippets/` → НЕ импортируются напрямую, это фрагменты для ручного
  переноса в `settings.py` проекта:
  - `settings_email_snippet.py` — SMTP (Gmail/Яндекс, App Password, .env).
  - `settings_i18n_snippet.py` — `LANGUAGES`, `LOCALE_PATHS`, `LocaleMiddleware`,
    3 способа переключения языка для API/SPA.

**Важно (i18n, уже задокументировано в коде, но держи в голове):**
язык должен быть активирован (`translation.activate(lang)`) ДО вызова
`calculate_esg_score()` / `generate_roadmap_from_answers()`, а не после. В
обычном request-cycle это делает `LocaleMiddleware` сам. Если PDF/email когда-
нибудь уйдут в Celery-таску — там активировать язык нужно будет вручную.

## locale/  — готовые переводы (en, kk), положить в корень Django-проекта
Django сам найдёт их через `LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]`
(см. `settings_i18n_snippet.py`). Ru отдельно не нужен — это язык-источник.

Проверено: 163/163 строки переведены на оба языка, пустых `msgstr` нет,
переключение языка на живом рендере шаблона работает корректно (проверял на
уровне и вопросов/секторов, и статичных подписей PDF-шаблона).

## data_exports/  — справочные экспорты в CSV
- `questions_for_db.csv` — 30 вопросов + 8 controversy-флагов, все поля модели
  Question (порядок, internal_code, block, text, question_type, weight,
  is_controversy, severity).
- `sectors_for_frontend.csv` — 14 секторов + под-отрасли, для дропдауна на
  фронтенде при регистрации компании.

## docs/
- `ESG_Методология_и_Анкета_ФИНАЛ.md` — полное описание методологии
  (источники синтеза LSEG/MSCI/S&P/Sustainalytics/Sustainable Fitch, формулы
  агрегации, тиры, роадмап).
- `esg_report_sample_en.pdf` — пример готового отчёта на английском, для
  демонстрации команде (полностью локализован, включая отрасль).

---
Всё в этом архиве прогнано и перепроверено: 39/39 тестов, компиляция и
рендер переводов на ru/en/kk, консистентность CSV ↔ esg_config.py ↔
question_type в populate_questions.py.
