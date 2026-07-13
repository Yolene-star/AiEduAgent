import asyncio

import httpx

from backend.app.main import app


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
        "used_card_ids": ["U1-C02", "U1-C04"],
        "next_actions": ["answer_check", "open_storybook"],
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
