import asyncio

import httpx
import pytest

from backend.app.main import app


@pytest.fixture(autouse=True)
def force_fake_provider(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "fake")


def request(method: str, path: str, **kwargs):
    async def _send():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_send())


def test_chat_returns_fixed_fake_answer_contract():
    response = request(
        "POST",
        "/api/v1/chat",
        json={"stage": "lower_primary", "message": "AI怎么认识小猫？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "answer": "它会从许多带有名字的小猫图片中学习共同特点。",
        "check_question": "图片旁边写着‘小猫’，这个名字在训练中叫什么？",
        "used_card_ids": ["U1-C04", "U1-C02"],
        "next_actions": ["answer_check", "open_storybook"],
        "sources": [
            {
                "card_id": "U1-C04",
                "title": "TensorFlow Image Classification",
                "url": "https://www.tensorflow.org/tutorials/images/classification",
            },
            {
                "card_id": "U1-C04",
                "title": "Google Supervised Learning",
                "url": "https://developers.google.com/machine-learning/intro-to-ml/supervised",
            },
            {
                "card_id": "U1-C02",
                "title": "Google Machine Learning Glossary",
                "url": "https://developers.google.com/machine-learning/glossary",
            },
        ],
    }
    assert isinstance(body["used_card_ids"], list)
    assert isinstance(body["next_actions"], list)


def test_chat_rejects_invalid_request_body():
    response = request("POST", "/api/v1/chat", json={"stage": "lower_primary"})

    assert response.status_code == 422


def test_chat_rejects_unknown_stage():
    response = request(
        "POST",
        "/api/v1/chat",
        json={"stage": "college", "message": "AI怎么认识小猫？"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "provider",
    ["fake_timeout", "fake_rate_limit", "fake_invalid_json"],
)
def test_chat_falls_back_when_provider_fails(monkeypatch, provider):
    monkeypatch.setenv("MODEL_PROVIDER", provider)

    response = request(
        "POST",
        "/api/v1/chat",
        json={"stage": "lower_primary", "message": "AI怎么认识小猫？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith("模型暂时不可用")
    assert body["next_actions"] == ["retry_later", "answer_check"]


def test_chat_returns_boundary_for_out_of_scope_question():
    response = request(
        "POST",
        "/api/v1/chat",
        json={"stage": "lower_primary", "message": "今天午饭吃什么？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["used_card_ids"] == []
    assert body["sources"] == []
    assert "不在 U1" in body["answer"]
