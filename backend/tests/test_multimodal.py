import asyncio

import httpx

from backend.app.main import app
from backend.app.multimodal import load_animation_spec, load_storybook_spec, validate_multimodal_assets


def request(method: str, path: str, **kwargs):
    async def _send():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_send())


def test_multimodal_specs_validate():
    validate_multimodal_assets()

    animation = load_animation_spec()
    storybook = load_storybook_spec()

    assert animation.template == "image_classification_process"
    assert [step.visual for step in animation.steps] == [
        "image-card",
        "pixel-grid",
        "feature-lines",
        "score-bars",
        "label-badge",
    ]
    assert len(storybook.pages) == 6
    assert all(page.alt for page in storybook.pages)
    assert all(page.image.startswith("/assets/storybook/") for page in storybook.pages)


def test_animation_endpoint_returns_data_only_spec():
    response = request("GET", "/api/v1/multimodal/animation/u1-image-classification")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "anim-u1-image-classification"
    assert "script" not in body
    assert len(body["steps"]) == 5


def test_storybook_endpoint_returns_six_reviewed_pages():
    response = request("GET", "/api/v1/multimodal/storybook/u1-lower-primary")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "storybook-u1-lower-primary"
    assert body["recommended_by_default"] is True
    assert [page["page"] for page in body["pages"]] == [1, 2, 3, 4, 5, 6]
    assert all(page["image"].endswith(".svg") for page in body["pages"])
