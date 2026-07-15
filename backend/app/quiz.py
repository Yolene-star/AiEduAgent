import json
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.knowledge import PROJECT_ROOT, filter_existing_card_ids
from backend.app.schemas import QuizQuestion, QuizSubmitRequest, QuizSubmitResponse


QUIZ_FILE = PROJECT_ROOT / "content" / "quizzes" / "u1_stage6.json"
DEMO_DATA_DIR = PROJECT_ROOT / "data" / "demo"
LEARNING_EVENTS_FILE = DEMO_DATA_DIR / "learning_events.jsonl"

QuestionType = Literal["multiple_choice", "true_false", "ordering"]
AnswerValue = str | bool | list[str]


class MisconceptionFeedback(BaseModel):
    error_type: str = Field(min_length=1)
    feedback: str = Field(min_length=1)


class FixedQuizQuestion(QuizQuestion):
    answer: AnswerValue
    explanation: str = Field(min_length=1)
    misconceptions: dict[str, MisconceptionFeedback] = Field(default_factory=dict)


class LearningEvent(BaseModel):
    event_id: str
    question_id: str
    student_id: str
    idempotency_key: str
    correct: bool
    error_type: str
    hints_used: int
    elapsed_ms: int
    answer: AnswerValue
    response: QuizSubmitResponse
    created_at: str


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache
def load_quizzes() -> dict[str, FixedQuizQuestion]:
    data = _load_json(QUIZ_FILE)
    if not isinstance(data, list):
        raise ValueError("u1_stage6.json must be a list")

    quizzes: dict[str, FixedQuizQuestion] = {}
    for item in data:
        question = FixedQuizQuestion.model_validate(item)
        if question.id in quizzes:
            raise ValueError(f"Duplicate quiz id: {question.id}")
        quizzes[question.id] = question

    if len(quizzes) != 20:
        raise ValueError(f"Expected 20 fixed quizzes, got {len(quizzes)}")

    expected_cards = {f"U1-C0{index}" for index in range(1, 6)}
    expected_stages = {"lower_primary", "upper_primary", "middle_school", "high_school"}
    coverage = {(question.card_id, question.stage) for question in quizzes.values()}
    expected_coverage = {(card_id, stage) for card_id in expected_cards for stage in expected_stages}
    if coverage != expected_coverage:
        raise ValueError("Fixed quizzes must cover 5 concepts x 4 stages")

    for question in quizzes.values():
        if question.card_id not in filter_existing_card_ids([question.card_id]):
            raise ValueError(f"Quiz {question.id} references missing card {question.card_id}")
        _validate_question_shape(question)

    return quizzes


def _validate_question_shape(question: FixedQuizQuestion) -> None:
    if question.quiz_type in {"multiple_choice", "true_false"} and question.items:
        raise ValueError(f"Quiz {question.id} should not have ordering items")
    if question.quiz_type == "ordering" and question.options:
        raise ValueError(f"Quiz {question.id} should not have choice options")
    if question.quiz_type == "multiple_choice":
        option_ids = [option.id for option in question.options]
        if not question.options or question.answer not in option_ids:
            raise ValueError(f"Quiz {question.id} has invalid multiple-choice answer")
    if question.quiz_type == "true_false" and not isinstance(question.answer, bool):
        raise ValueError(f"Quiz {question.id} must use boolean answer")
    if question.quiz_type == "ordering":
        item_ids = [item.id for item in question.items]
        if sorted(question.answer) != sorted(item_ids):  # type: ignore[arg-type]
            raise ValueError(f"Quiz {question.id} has invalid ordering answer")


def list_quiz_questions(stage: str | None = None) -> list[QuizQuestion]:
    questions = load_quizzes().values()
    if stage:
        questions = [question for question in questions if question.stage == stage]
    return [
        QuizQuestion.model_validate(question.model_dump(exclude={"answer", "explanation", "misconceptions"}))
        for question in questions
    ]


def get_quiz_question(question_id: str) -> FixedQuizQuestion:
    quizzes = load_quizzes()
    if question_id not in quizzes:
        raise KeyError(question_id)
    return quizzes[question_id]


def grade_quiz(question_id: str, submission: QuizSubmitRequest) -> QuizSubmitResponse:
    existing = find_event_by_idempotency_key(submission.student_id, submission.idempotency_key)
    if existing:
        response = existing.response.model_copy(update={"already_recorded": True})
        return response

    question = get_quiz_question(question_id)
    _validate_submission_answer(question, submission.answer)
    correct = submission.answer == question.answer
    error_type = "none" if correct else _error_type_for_answer(question, submission.answer)
    explanation = question.explanation if correct else _feedback_for_answer(question, submission.answer)
    response = QuizSubmitResponse(
        question_id=question.id,
        correct=correct,
        explanation=explanation,
        error_type=error_type,
        review_card_id=question.review_card_id,
        next_actions=["next_quiz"] if correct else ["review_card", "retry_quiz"],
    )
    event = LearningEvent(
        event_id=str(uuid4()),
        question_id=question.id,
        student_id=submission.student_id,
        idempotency_key=submission.idempotency_key,
        correct=correct,
        error_type=error_type,
        hints_used=submission.hints_used,
        elapsed_ms=submission.elapsed_ms,
        answer=submission.answer,
        response=response,
        created_at=datetime.now(UTC).isoformat(),
    )
    append_learning_event(event)
    return response


def _validate_submission_answer(question: FixedQuizQuestion, answer: AnswerValue) -> None:
    if question.quiz_type == "multiple_choice":
        option_ids = {option.id for option in question.options}
        if not isinstance(answer, str) or answer not in option_ids:
            raise ValueError("invalid_option")
    elif question.quiz_type == "true_false":
        if not isinstance(answer, bool):
            raise ValueError("invalid_boolean")
    elif question.quiz_type == "ordering":
        item_ids = {item.id for item in question.items}
        if not isinstance(answer, list) or set(answer) != item_ids or len(answer) != len(item_ids):
            raise ValueError("invalid_ordering")


def _error_type_for_answer(question: FixedQuizQuestion, answer: AnswerValue) -> str:
    key = _answer_key(answer)
    feedback = question.misconceptions.get(key) or question.misconceptions.get("default")
    return feedback.error_type if feedback else "wrong_answer"


def _feedback_for_answer(question: FixedQuizQuestion, answer: AnswerValue) -> str:
    key = _answer_key(answer)
    feedback = question.misconceptions.get(key) or question.misconceptions.get("default")
    if feedback:
        return feedback.feedback
    return f"还不对。可以回看 {question.review_card_id}，再试一次。"


def _answer_key(answer: AnswerValue) -> str:
    if isinstance(answer, bool):
        return str(answer).lower()
    if isinstance(answer, list):
        return ",".join(answer)
    return answer


def append_learning_event(event: LearningEvent) -> None:
    LEARNING_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LEARNING_EVENTS_FILE.open("a", encoding="utf-8") as file:
        file.write(event.model_dump_json())
        file.write("\n")


def read_learning_events() -> list[LearningEvent]:
    if not LEARNING_EVENTS_FILE.exists():
        return []
    events: list[LearningEvent] = []
    with LEARNING_EVENTS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                events.append(LearningEvent.model_validate_json(line))
    return events


def find_event_by_idempotency_key(student_id: str, idempotency_key: str) -> LearningEvent | None:
    for event in read_learning_events():
        if event.student_id == student_id and event.idempotency_key == idempotency_key:
            return event
    return None


def reset_demo_data() -> None:
    LEARNING_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LEARNING_EVENTS_FILE.exists():
        LEARNING_EVENTS_FILE.unlink()
    students_file = LEARNING_EVENTS_FILE.parent / "demo_students.json"
    students_file.write_text(
        json.dumps(
            [
                {"student_id": "demo-lower-primary", "stage": "lower_primary", "interest": "animals"},
                {"student_id": "demo-high-school", "stage": "high_school", "interest": "programming"},
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
