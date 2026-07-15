import pytest

from backend.app.knowledge import load_cards
from backend.app.schemas import Stage
from backend.app.stage_policy import (
    get_stage_policy,
    render_stage_explanation,
    validate_stage_output,
)


STAGES: list[Stage] = ["lower_primary", "upper_primary", "middle_school", "high_school"]


@pytest.mark.parametrize("card_id", sorted(load_cards()))
@pytest.mark.parametrize("stage", STAGES)
def test_twenty_stage_concept_baselines_pass_format_rules(stage, card_id):
    answer, check_question, _actions = render_stage_explanation(stage, card_id)
    result = validate_stage_output(
        answer=answer,
        check_question=check_question,
        policy=get_stage_policy(stage),
    )

    assert result.is_valid, result.errors


def test_format_validator_detects_too_long_answer():
    policy = get_stage_policy("lower_primary")
    result = validate_stage_output(
        answer="像素" * 200,
        check_question="这是什么？",
        policy=policy,
    )

    assert "answer_too_long:400" in result.errors


def test_format_validator_detects_too_many_terms():
    policy = get_stage_policy("lower_primary")
    result = validate_stage_output(
        answer="像素 标签 训练数据 图像分类 " * 20,
        check_question="这是什么？",
        policy=policy,
    )

    assert any(error.startswith("too_many_terms") for error in result.errors)


def test_format_validator_detects_illegal_formula_for_lower_primary():
    policy = get_stage_policy("lower_primary")
    result = validate_stage_output(
        answer="小猫看图片。" * 20 + " accuracy = right / total",
        check_question="这是什么？",
        policy=policy,
    )

    assert "formula_not_allowed" in result.errors


def test_check_understanding_allows_only_one_question_for_each_stage():
    for stage in STAGES:
        answer, _question, _actions = render_stage_explanation(stage, "U1-C04")
        result = validate_stage_output(
            answer=answer,
            check_question="第一题？第二题？",
            policy=get_stage_policy(stage),
        )
        assert "wrong_question_count:2" in result.errors
