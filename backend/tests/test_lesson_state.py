import pytest

from backend.app.lesson_state import (
    InvalidLessonTransition,
    LessonEvent,
    LessonState,
    transition_state,
)


def test_happy_path_state_machine():
    state = LessonState.WELCOME
    state = transition_state(state, LessonEvent.START)
    assert state == LessonState.DIAGNOSE
    state = transition_state(state, LessonEvent.DIAGNOSIS_DONE)
    assert state == LessonState.EXPLAIN
    state = transition_state(state, LessonEvent.EXPLANATION_DONE)
    assert state == LessonState.CHECK_UNDERSTANDING
    state = transition_state(state, LessonEvent.CHECK_ANSWER_CORRECT)
    assert state == LessonState.PRACTICE
    state = transition_state(state, LessonEvent.PRACTICE_DONE)
    assert state == LessonState.REFLECT
    state = transition_state(state, LessonEvent.REFLECTION_DONE)
    assert state == LessonState.RECOMMEND


def test_wrong_answer_enters_remediation_then_rechecks():
    state = transition_state(
        LessonState.CHECK_UNDERSTANDING,
        LessonEvent.CHECK_ANSWER_WRONG,
    )
    assert state == LessonState.REMEDIATE

    state = transition_state(state, LessonEvent.REMEDIATION_DONE)
    assert state == LessonState.CHECK_UNDERSTANDING


def test_model_cannot_jump_from_welcome_to_recommend():
    with pytest.raises(InvalidLessonTransition):
        transition_state(LessonState.WELCOME, LessonEvent.REFLECTION_DONE)
