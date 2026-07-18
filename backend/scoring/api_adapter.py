"""
api_adapter.py — адаптер между нашей ESG-методологией (esg_config.py) и контрактом API,
описанным в ТЗ команды (раздел 4.5 "Result" и раздел 5.5 "Примеры данных").

ВАЖНО: этот файл НЕ меняет esg_config.py и report_generator.py — методология,
10 категорий, 5 тиров, industry-weighted веса остаются как есть. Здесь только
"перевод" уже посчитанного результата в форму, которую ожидает фронтенд по ТЗ.

Используй эти функции в DRF-views вместо того, чтобы отдавать result/roadmap
из esg_config.py напрямую в Response().
"""

from .esg_config import CATEGORY_PILLAR


# ============================================================
# 1. Уровень компании по шкале ТЗ (0-40/41-60/61-80/81-100)
#    Считается напрямую по числу esg_final, НЕ через наши TIERS —
#    поэтому наша 5-тирная система внутри остаётся нетронутой,
#    а наружу для контракта ТЗ отдаётся именно её терминология.
# ============================================================

def get_tz_level(score: float) -> str:
    """Возвращает уровень строго по границам из ТЗ (раздел 3.5), а не по нашим TIERS."""
    if score >= 81:
        return "Лидер"
    if score >= 61:
        return "Продвинутый"
    if score >= 41:
        return "Развивающийся"
    return "Начальный"


# ============================================================
# 2. Роадмап -> плоские списки строк по E/S/G (раздел 5.5 ТЗ)
# ============================================================

def adapt_roadmap_to_tz_format(roadmap: dict) -> dict:
    """
    Наш generate_roadmap()/generate_roadmap_from_answers() группирует рекомендации
    по 10 категориям и по горизонту внедрения (quick/mid/long).
    ТЗ ожидает простой словарь {"E": [...], "S": [...], "G": [...]} со строками.

    Сортируем внутри каждого пилара по priority_score (уже посчитан нашей методологией),
    чтобы самые приоритетные рекомендации шли первыми в списке — это не теряется
    при "уплощении" структуры.
    """
    grouped = {"E": [], "S": [], "G": []}

    for rec in roadmap.get("all_recommendations", []):
        pillar = rec.get("pillar") or CATEGORY_PILLAR.get(rec["category"])
        if pillar in grouped:
            grouped[pillar].append(rec)

    for pillar in grouped:
        grouped[pillar].sort(key=lambda r: r["priority_score"], reverse=True)
        grouped[pillar] = [r["text"] for r in grouped[pillar]]

    return grouped


# ============================================================
# 3. Полный результат -> формат ТЗ
# ============================================================

def adapt_result_to_tz_format(result: dict, roadmap: dict, company_name: str = None) -> dict:
    """
    Собирает ответ ровно в форме, которую ожидает GET /api/v1/result/{id}/ по ТЗ:

    {
        "company_name": "...",
        "score_e": 65.0,
        "score_s": 80.0,
        "score_g": 50.0,
        "score_total": 65.0,
        "level": "Тир 2 — Продвинутый",
        "recommendations": {"E": [...], "S": [...], "G": [...]}
    }

    ОБНОВЛЕНО: поле "level" теперь отдаёт нашу 5-уровневую систему (result["tier"]),
    а не 4-уровневую из исходного ТЗ — сохраняем нашу методологию
    как есть и на уровне API, а не только внутри. Функция get_tz_level() оставлена
    в файле на случай, если где-то в будущем понадобится именно 4-уровневая версия
    (например, для сравнения/отчётности), но в основном ответе API больше не используется.

    Ничего не пересчитывает — только переупаковывает уже готовый result/roadmap
    из esg_config.py. Наш более подробный формат (pillar_scores, category_scores,
    controversy_warnings, horizon-группировка и т.д.) никуда не девается —
    его можно хранить в БД целиком (например, в JSONField) и отдавать отдельным
    "расширенным" эндпоинтом для админ-дашборда, где детализация полезна.
    """
    return {
        "company_name": company_name,
        "score_e": round(result["pillar_scores"]["E"], 1),
        "score_s": round(result["pillar_scores"]["S"], 1),
        "score_g": round(result["pillar_scores"]["G"], 1),
        "score_total": result["esg_final"],
        "level": result["tier"],  # наши 5 тиров напрямую, вместо get_tz_level()
        "recommendations": adapt_roadmap_to_tz_format(roadmap),
    }
