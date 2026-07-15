from enum import Enum


class LessonState(str, Enum):
    WELCOME = "WELCOME"
    DIAGNOSE = "DIAGNOSE"
    EXPLAIN = "EXPLAIN"
    CHECK_UNDERSTANDING = "CHECK_UNDERSTANDING"
    PRACTICE = "PRACTICE"
    REFLECT = "REFLECT"
    RECOMMEND = "RECOMMEND"
    REMEDIATE = "REMEDIATE"


class LessonEvent(str, Enum):
    START = "START"
    DIAGNOSIS_DONE = "DIAGNOSIS_DONE"
    EXPLANATION_DONE = "EXPLANATION_DONE"
    CHECK_ANSWER_CORRECT = "CHECK_ANSWER_CORRECT"
    CHECK_ANSWER_WRONG = "CHECK_ANSWER_WRONG"
    PRACTICE_DONE = "PRACTICE_DONE"
    REFLECTION_DONE = "REFLECTION_DONE"
    REMEDIATION_DONE = "REMEDIATION_DONE"


ALLOWED_TRANSITIONS: dict[tuple[LessonState, LessonEvent], LessonState] = {
    (LessonState.WELCOME, LessonEvent.START): LessonState.DIAGNOSE,
    (LessonState.DIAGNOSE, LessonEvent.DIAGNOSIS_DONE): LessonState.EXPLAIN,
    (LessonState.EXPLAIN, LessonEvent.EXPLANATION_DONE): LessonState.CHECK_UNDERSTANDING,
    (LessonState.CHECK_UNDERSTANDING, LessonEvent.CHECK_ANSWER_CORRECT): LessonState.PRACTICE,
    (LessonState.CHECK_UNDERSTANDING, LessonEvent.CHECK_ANSWER_WRONG): LessonState.REMEDIATE,
    (LessonState.PRACTICE, LessonEvent.PRACTICE_DONE): LessonState.REFLECT,
    (LessonState.REFLECT, LessonEvent.REFLECTION_DONE): LessonState.RECOMMEND,
    (LessonState.REMEDIATE, LessonEvent.REMEDIATION_DONE): LessonState.CHECK_UNDERSTANDING,
}


class InvalidLessonTransition(ValueError):
    pass


def transition_state(current_state: LessonState, event: LessonEvent) -> LessonState:
    next_state = ALLOWED_TRANSITIONS.get((current_state, event))
    if next_state is None:
        raise InvalidLessonTransition(f"Cannot transition from {current_state} with {event}")
    return next_state


def default_event_for_state(current_state: LessonState) -> LessonEvent:
    defaults = {
        LessonState.WELCOME: LessonEvent.START,
        LessonState.DIAGNOSE: LessonEvent.DIAGNOSIS_DONE,
        LessonState.EXPLAIN: LessonEvent.EXPLANATION_DONE,
        LessonState.CHECK_UNDERSTANDING: LessonEvent.CHECK_ANSWER_CORRECT,
        LessonState.PRACTICE: LessonEvent.PRACTICE_DONE,
        LessonState.REFLECT: LessonEvent.REFLECTION_DONE,
        LessonState.REMEDIATE: LessonEvent.REMEDIATION_DONE,
    }
    return defaults.get(current_state, LessonEvent.START)
