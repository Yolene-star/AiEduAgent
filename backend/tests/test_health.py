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


def test_health_returns_ok():
    response = request("GET", "/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_are_available():
    response = request("GET", "/docs")

    assert response.status_code == 200


def test_request_id_header_is_returned():
    response = request("GET", "/health", headers={"x-request-id": "stage-1-test"})

    assert response.headers["x-request-id"] == "stage-1-test"
