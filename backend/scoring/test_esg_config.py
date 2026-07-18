"""
tests/test_esg_config.py — unit-тесты для esg_config.py.

Запуск: pytest tests/test_esg_config.py -v
(нужен pytest: pip install pytest)

Служит доказательством, что методология считает баллы корректно
(веса секторов суммируются в 1.0, disclosure gate и controversy cap работают по правилам).
Замена ручному smoke-test (print+json.dumps) — теперь каждое поведение
проверяется отдельным тестом с понятным assert, и pytest сам покажет,
что именно сломалось, если сломалось.
"""

import pytest

from esg_config import (
    QUESTIONS,
    SECTORS,
    SUB_INDUSTRIES,
    normalize_answer,
    calculate_category_and_pillar_scores,
    get_weights,
    calculate_controversy_cap,
    get_tier,
    calculate_esg_score,
)


# ============================================================
# normalize_answer
# ============================================================

class TestNormalizeAnswer:

    def test_scale_question_returns_value_as_is(self):
        question = {"type": "scale"}
        assert normalize_answer(question, 75) == 75.0

    def test_scale_question_clamps_above_100(self):
        question = {"type": "scale"}
        assert normalize_answer(question, 150) == 100.0

    def test_scale_question_clamps_below_0(self):
        question = {"type": "scale"}
        assert normalize_answer(question, -10) == 0.0

    def test_percent_question_at_min_returns_0(self):
        question = {"type": "percent", "min": 0, "target": 100}
        assert normalize_answer(question, 0) == 0.0

    def test_percent_question_at_target_returns_100(self):
        question = {"type": "percent", "min": 0, "target": 100}
        assert normalize_answer(question, 100) == 100.0

    def test_percent_question_linear_interpolation(self):
        question = {"type": "percent", "min": 0, "target": 100}
        assert normalize_answer(question, 50) == 50.0

    def test_percent_question_custom_target(self):
        # E3_1: доля зелёной выручки, target=30 (не 100)
        question = {"type": "percent", "min": 0, "target": 30}
        assert normalize_answer(question, 30) == 100.0
        assert normalize_answer(question, 15) == 50.0

    def test_none_answer_returns_none(self):
        question = {"type": "scale"}
        assert normalize_answer(question, None) is None

    def test_empty_string_answer_returns_none(self):
        question = {"type": "scale"}
        assert normalize_answer(question, "") is None


# ============================================================
# calculate_category_and_pillar_scores
# ============================================================

class TestCategoryAndPillarScores:

    def test_all_answers_75_gives_all_categories_75(self):
        # Для percent-вопросов (например, E3_1 с target=30) ответ "75" — это не 75% от шкалы,
        # а сырое значение, которое нормализуется через min/target. Чтобы каждый вопрос дал
        # ровно 75 баллов после нормализации, нужно подавать разное сырое значение
        # для scale и percent вопросов.
        answers = {}
        for q in QUESTIONS:
            if q["type"] == "scale":
                answers[q["id"]] = 75
            else:  # percent
                answers[q["id"]] = q["min"] + 0.75 * (q["target"] - q["min"])

        category_scores, pillar_scores, disclosure_flags = calculate_category_and_pillar_scores(answers)

        for cat_id, score in category_scores.items():
            assert score == pytest.approx(75.0), f"Category {cat_id} expected 75, got {score}"

        assert pillar_scores["E"] == pytest.approx(75.0)
        assert pillar_scores["S"] == pytest.approx(75.0)
        assert pillar_scores["G"] == pytest.approx(75.0)

    def test_no_disclosure_flag_when_all_answered(self):
        answers = {q["id"]: 75 for q in QUESTIONS}
        _, _, disclosure_flags = calculate_category_and_pillar_scores(answers)
        assert all(flag is False for flag in disclosure_flags.values())

    def test_disclosure_gate_triggers_below_50_percent(self):
        # E1 категория имеет 4 вопроса — отвечаем только на 1 из 4 (25% < 50%)
        answers = {"E1_1": 100}
        category_scores, _, disclosure_flags = calculate_category_and_pillar_scores(answers)

        assert disclosure_flags["E1"] is True
        # avg=100, но множитель 0.8 из-за disclosure gate -> 80
        assert category_scores["E1"] == pytest.approx(80.0)

    def test_disclosure_gate_not_triggered_at_exactly_50_percent(self):
        # E1 категория имеет 4 вопроса — отвечаем на 2 из 4 (ровно 50%, порог "< 50%" не срабатывает)
        answers = {"E1_1": 100, "E1_2": 100}
        category_scores, _, disclosure_flags = calculate_category_and_pillar_scores(answers)

        assert disclosure_flags["E1"] is False
        assert category_scores["E1"] == pytest.approx(100.0)

    def test_empty_answers_gives_zero_scores(self):
        category_scores, pillar_scores, disclosure_flags = calculate_category_and_pillar_scores({})
        assert all(score == 0.0 for score in category_scores.values())
        assert all(flag is True for flag in disclosure_flags.values())


# ============================================================
# get_weights
# ============================================================

class TestGetWeights:

    def test_sector_only_returns_sector_weights(self):
        weights = get_weights("tech")
        expected = next(s["weights"] for s in SECTORS if s["id"] == "tech")
        assert weights == expected

    def test_subindustry_overrides_sector_weights(self):
        sector_weights = get_weights("tech")
        sub_weights = get_weights("tech", "software")
        assert sub_weights != sector_weights
        expected = next(s["weights"] for s in SUB_INDUSTRIES["tech"] if s["id"] == "software")
        assert sub_weights == expected

    def test_unknown_subindustry_falls_back_to_sector(self):
        weights = get_weights("tech", "nonexistent_sub")
        expected = next(s["weights"] for s in SECTORS if s["id"] == "tech")
        assert weights == expected

    def test_unknown_sector_falls_back_to_other(self):
        weights = get_weights("nonexistent_sector")
        expected = next(s["weights"] for s in SECTORS if s["id"] == "other")
        assert weights == expected

    def test_all_sector_weights_sum_to_one(self):
        for sector in SECTORS:
            total = sum(sector["weights"].values())
            assert total == pytest.approx(1.0), f"Sector {sector['id']} weights don't sum to 1.0"

    def test_all_subindustry_weights_sum_to_one(self):
        for sector_id, subs in SUB_INDUSTRIES.items():
            for sub in subs:
                total = sum(sub["weights"].values())
                assert total == pytest.approx(1.0), f"Sub-industry {sector_id}/{sub['id']} weights don't sum to 1.0"


# ============================================================
# calculate_controversy_cap
# ============================================================

class TestControversyCap:

    def test_no_flags_no_cap(self):
        result = calculate_controversy_cap({})
        assert result["severity"] == 0
        assert result["cap"] == 100

    def test_single_low_severity_flag(self):
        result = calculate_controversy_cap({"C7": True})  # severity 1
        assert result["severity"] == 1
        assert result["cap"] == 90

    def test_critical_flag_caps_at_35(self):
        result = calculate_controversy_cap({"C1": True})  # severity 4
        assert result["severity"] == 4
        assert result["cap"] == 35

    def test_takes_maximum_severity_among_multiple_flags(self):
        result = calculate_controversy_cap({"C7": True, "C4": True, "C1": True})  # severities 1, 2, 4
        assert result["severity"] == 4
        assert result["cap"] == 35

    def test_false_flags_are_ignored(self):
        result = calculate_controversy_cap({"C1": False, "C4": False})
        assert result["severity"] == 0
        assert result["cap"] == 100


# ============================================================
# get_tier
# ============================================================

class TestGetTier:

    @pytest.mark.parametrize("score,expected_substring", [
        (100, "Лидирующий"),
        (85, "Лидирующий"),
        (84.9, "Продвинутый"),
        (70, "Продвинутый"),
        (69.9, "Развивающийся"),
        (55, "Развивающийся"),
        (54.9, "Базовый"),
        (40, "Базовый"),
        (39.9, "Отстающий"),
        (0, "Отстающий"),
    ])
    def test_tier_boundaries(self, score, expected_substring):
        assert expected_substring in get_tier(score)


# ============================================================
# calculate_esg_score (интеграционный тест всего пайплайна)
# ============================================================

class TestCalculateESGScore:

    def test_full_pipeline_with_uniform_answers(self):
        answers = {}
        for q in QUESTIONS:
            if q["type"] == "scale":
                answers[q["id"]] = 75
            else:
                answers[q["id"]] = q["min"] + 0.75 * (q["target"] - q["min"])

        result = calculate_esg_score(
            answers=answers,
            controversy_answers={},
            sector_id="tech",
            sub_industry_id="software",
        )
        assert result["esg_final"] == pytest.approx(75.0, abs=0.1)
        assert result["controversy_severity"] == 0
        assert "Продвинутый" in result["tier"]

    def test_controversy_flag_caps_final_score(self):
        # Все ответы = 100 (без cap скор был бы 100), но C1 (severity 4) должен закапать на 35
        answers = {q["id"]: 100 for q in QUESTIONS}
        result = calculate_esg_score(
            answers=answers,
            controversy_answers={"C1": True},
            sector_id="tech",
        )
        assert result["esg_raw"] == pytest.approx(100.0, abs=0.1)
        assert result["esg_final"] == 35.0
        assert "Отстающий" in result["tier"]

    def test_missing_answers_reduce_score_via_disclosure_gate(self):
        result_full = calculate_esg_score(
            answers={q["id"]: 100 for q in QUESTIONS},
            controversy_answers={},
            sector_id="other",
        )
        result_partial = calculate_esg_score(
            answers={"E1_1": 100},  # почти всё не отвечено
            controversy_answers={},
            sector_id="other",
        )
        assert result_partial["esg_final"] < result_full["esg_final"]

    def test_sector_weights_affect_final_score(self):
        # Разброс: E1/E2/E3 (Environment) низкие, остальное высокое.
        # На "energy" секторе (вес E=55%) это должно сильнее просадить итог, чем на "financial" (вес E=10%).
        answers = {q["id"]: 90 for q in QUESTIONS}
        for q in QUESTIONS:
            if q["pillar"] == "E":
                answers[q["id"]] = 20

        result_energy = calculate_esg_score(answers, {}, sector_id="energy")
        result_financial = calculate_esg_score(answers, {}, sector_id="financial")

        assert result_energy["esg_final"] < result_financial["esg_final"]
