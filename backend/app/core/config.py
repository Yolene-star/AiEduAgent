from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "AiEduAgent"
    app_version: str = "0.1.0"
    dify_base_url: str = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
    dify_api_key: str = os.getenv("DIFY_API_KEY", "")
    dify_app_id: str = os.getenv("DIFY_APP_ID", "")
    dify_timeout_seconds: int = int(os.getenv("DIFY_TIMEOUT_SECONDS", "20"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
