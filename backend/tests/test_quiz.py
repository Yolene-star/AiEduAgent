import asyncio
from uuid import uuid4

import httpx
import pytest

from backend.app import quiz
from backend.app.main import app
from backend.app.quiz import load_quizzes, read_learning_events


@pytest.fixture(autouse=True)
def isolate_learning_events(tmp_path, monkeypatch):
    monkeypatch.setattr(quiz, "LEARNING_EVENTS_FILE", tmp_path / "learning_events.jsonl")


def request(method: str, path: str, **kwargs):
    async def _send():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_send())


def submit_payload(answer, *, idempotency_key: str | None = None):
    return {
        "student_id": "demo-student",
        "answer": answer,
        "hints_used": 1,
        "elapsed_ms": 1200,
        "idempotency_key": idempotency_key or f"test-{uuid4()}",
    }


def test_fixed_quiz_bank_has_20_questions_and_hides_answers():
    response = request("GET", "/api/v1/quizzes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 20
    assert {item["stage"] for item in body} == {
        "lower_primary",
        "upper_primary",
        "middle_school",
        "high_school",
    }
    assert all("answer" not in item for item in body)


@pytest.mark.parametrize("question", list(load_quizzes().values()), ids=lambda question: question.id)
def test_all_fixed_quizzes_grade_correct_answers(question):
    response = request(
        "POST",
        f"/api/v1/quiz/{question.id}/submit",
        json=submit_payload(question.answer),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is True
    assert body["error_type"] == "none"
    assert body["review_card_id"] == question.review_card_id
    assert body["already_recorded"] is False
    assert read_learning_events()[0].correct is True


def test_wrong_answer_returns_misconception_feedback():
    response = request(
        "POST",
        "/api/v1/quiz/U1-C02-upper_primary-tf/submit",
        json=submit_payload(True),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is False
    assert body["error_type"] == "label_quality"
    assert "随便的标签会误导模型" in body["explanation"]
    assert body["next_actions"] == ["review_card", "retry_quiz"]


def test_duplicate_submit_with_same_idempotency_key_does_not_duplicate_event():
    idempotency_key = "same-click-0001"

    first = request(
        "POST",
        "/api/v1/quiz/U1-C01-lower_primary-mc/submit",
        json=submit_payload("A", idempotency_key=idempotency_key),
    )
    second = request(
        "POST",
        "/api/v1/quiz/U1-C01-lower_primary-mc/submit",
        json=submit_payload("B", idempotency_key=idempotency_key),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["correct"] is True
    assert second.json()["correct"] is True
    assert second.json()["already_recorded"] is True
    assert len(read_learning_events()) == 1


def test_invalid_option_is_rejected_and_not_recorded():
    response = request(
        "POST",
        "/api/v1/quiz/U1-C01-lower_primary-mc/submit",
        json=submit_payload("Z"),
    )

    assert response.status_code == 422
    assert read_learning_events() == []


def test_learning_event_persists_after_second_read():
    response = request(
        "POST",
        "/api/v1/quiz/U1-C05-high_school-tf/submit",
        json=submit_payload(True),
    )

    assert response.status_code == 200
    first_read = read_learning_events()
    second_read = read_learning_events()
    assert len(first_read) == 1
    assert second_read[0].question_id == "U1-C05-high_school-tf"
    assert second_read[0].hints_used == 1
    assert second_read[0].elapsed_ms == 1200
