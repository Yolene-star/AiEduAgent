import os

from backend.app.providers.base import ModelProvider, ModelProviderError
from backend.app.providers.fake import FakeModelProvider
from backend.app.providers.real import RealModelProvider


def get_model_provider() -> ModelProvider:
    provider = os.getenv("MODEL_PROVIDER", "fake").strip().lower()

    if provider == "fake":
        return FakeModelProvider()
    if provider == "fake_timeout":
        return FakeModelProvider(failure_mode="timeout")
    if provider == "fake_rate_limit":
        return FakeModelProvider(failure_mode="rate_limit")
    if provider == "fake_invalid_json":
        return FakeModelProvider(failure_mode="invalid_json")
    if provider == "real":
        api_key = os.getenv("LLM_API_KEY", "")
        if not api_key or api_key == "replace_me":
            raise ModelProviderError("LLM_API_KEY is required for real provider", status="missing_config")

        return RealModelProvider(
            api_key=api_key,
            model_alias=os.getenv("LLM_MODEL", "replace_me"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
            timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "20")),
        )

    raise ModelProviderError(f"Unknown MODEL_PROVIDER: {provider}", status="missing_config")
