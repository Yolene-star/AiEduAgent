import asyncio
import json

import httpx
import pytest

from backend.app.providers import FakeModelProvider, ModelProviderError, RealModelProvider
from backend.app.providers.factory import get_model_provider
from backend.app.schemas import TutorGenerationRequest


def run(coro):
    return asyncio.run(coro)


def generation_request() -> TutorGenerationRequest:
    return TutorGenerationRequest(
        stage="lower_primary",
        message="AI怎么认识小猫？",
        request_id="stage-3-test",
    )


def model_response(data: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "content": json.dumps(data, ensure_ascii=False),
                    }
                }
            ]
        },
    )


def real_provider(handler) -> RealModelProvider:
    return RealModelProvider(
        api_key="test-key",
        model_alias="test-model",
        base_url="https://model.example/v1",
        timeout_seconds=0.1,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )


def test_fake_provider_generates_fixed_structured_output():
    provider = FakeModelProvider()

    result = run(provider.generate(generation_request()))

    assert "标签" in result.answer
    assert result.used_card_ids == ["U1-C02", "U1-C04"]
    assert result.teaching_form == "storybook"


def test_factory_defaults_to_fake_without_api_key(monkeypatch):
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    provider = get_model_provider()

    assert isinstance(provider, FakeModelProvider)


def test_factory_real_provider_requires_api_key(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "real")
    monkeypatch.setenv("LLM_API_KEY", "replace_me")

    with pytest.raises(ModelProviderError) as exc_info:
        get_model_provider()

    assert exc_info.value.status == "missing_config"


def test_factory_real_provider_uses_environment(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "real")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_BASE_URL", "https://model.example/v1")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "3")

    provider = get_model_provider()

    assert isinstance(provider, RealModelProvider)
    assert provider.model_alias == "test-model"
    assert provider.base_url == "https://model.example/v1"
    assert provider.timeout_seconds == 3


def test_real_provider_accepts_valid_structured_output():
    captured_payload = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
        captured_payload.update(json.loads(request.content))
        return model_response(
            {
                "answer": "结构化回答",
                "check_question": "检查题？",
                "used_card_ids": ["U1-C02"],
                "next_actions": ["answer_check"],
                "teaching_form": "quick_quiz",
            }
        )

    provider = real_provider(handler)

    result = run(provider.generate(generation_request()))

    assert result.answer == "结构化回答"
    assert result.used_card_ids == ["U1-C02"]
    assert captured_payload["response_format"] == {"type": "json_object"}
    assert captured_payload["max_tokens"] == 800
    assert "json" in captured_payload["messages"][0]["content"].lower()
    assert "teaching_form" in captured_payload["messages"][0]["content"]


def test_real_provider_timeout_is_controlled():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("too slow")

    provider = real_provider(handler)

    with pytest.raises(ModelProviderError) as exc_info:
        run(provider.generate(generation_request()))

    assert exc_info.value.status == "timeout"


def test_real_provider_http_error_keeps_safe_detail():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "bad request"}})

    provider = real_provider(handler)

    with pytest.raises(ModelProviderError) as exc_info:
        run(provider.generate(generation_request()))

    assert exc_info.value.status == "http_error"
    assert "http_400" in (exc_info.value.detail or "")
    assert "test-key" not in (exc_info.value.detail or "")


def test_real_provider_retries_rate_limit_once():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(429, json={"error": "rate limit"})
        return model_response(
            {
                "answer": "重试后成功",
                "check_question": "检查题？",
                "used_card_ids": ["U1-C02"],
                "next_actions": ["answer_check"],
                "teaching_form": "quick_quiz",
            }
        )

    provider = real_provider(handler)

    result = run(provider.generate(generation_request()))

    assert calls["count"] == 2
    assert result.answer == "重试后成功"


def test_real_provider_rejects_invalid_json():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "not-json"}}]},
        )

    provider = real_provider(handler)

    with pytest.raises(ModelProviderError) as exc_info:
        run(provider.generate(generation_request()))

    assert exc_info.value.status == "invalid_json"


def test_real_provider_rejects_empty_content():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": ""}}]},
        )

    provider = real_provider(handler)

    with pytest.raises(ModelProviderError) as exc_info:
        run(provider.generate(generation_request()))

    assert exc_info.value.status == "empty_content"


def test_real_provider_rejects_empty_answer():
    def handler(request: httpx.Request) -> httpx.Response:
        return model_response(
            {
                "answer": "",
                "check_question": "检查题？",
                "used_card_ids": ["U1-C02"],
                "next_actions": ["answer_check"],
            }
        )

    provider = real_provider(handler)

    with pytest.raises(ModelProviderError) as exc_info:
        run(provider.generate(generation_request()))

    assert exc_info.value.status == "invalid_json"
