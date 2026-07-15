import asyncio

import httpx
import pytest

from backend.app import resources as resource_store
from backend.app.main import app


@pytest.fixture(autouse=True)
def isolate_resource_drafts(tmp_path, monkeypatch):
    monkeypatch.setattr(resource_store, "RESOURCE_DRAFTS_FILE", tmp_path / "course_resources.jsonl")


def request(method: str, path: str, **kwargs):
    async def _send():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_send())


def resource_payload(**overrides):
    payload = {
        "title": "图像分类补充阅读",
        "resource_type": "link",
        "stage": "middle_school",
        "unit": "U1",
        "topic": "图像分类",
        "source_url": "https://example.edu/image-classification",
        "license": "teacher-reviewed-demo",
        "description": "后续可审核进入课程库的补充链接。",
        "card_ids": ["U1-C04"],
        "created_by": "demo-teacher",
    }
    payload.update(overrides)
    return payload


def test_add_course_resource_creates_draft_record():
    response = request("POST", "/api/v1/resources", json=resource_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("res-")
    assert body["status"] == "draft"
    assert body["card_ids"] == ["U1-C04"]
    assert body["title"] == "图像分类补充阅读"


def test_list_course_resources_reads_persisted_drafts():
    created = request("POST", "/api/v1/resources", json=resource_payload()).json()

    response = request("GET", "/api/v1/resources")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created["id"]


def test_add_course_resource_rejects_unknown_card_id():
    response = request("POST", "/api/v1/resources", json=resource_payload(card_ids=["BAD-CARD"]))

    assert response.status_code == 422
    assert "unknown card_id" in response.json()["detail"]
