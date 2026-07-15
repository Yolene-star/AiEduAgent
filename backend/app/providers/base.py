from typing import Protocol

from backend.app.schemas import TutorGenerationRequest, TutorGenerationResponse


class ModelProviderError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status: str = "error",
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.detail = detail


class ModelProvider(Protocol):
    provider_name: str
    model_alias: str

    async def generate(self, request: TutorGenerationRequest) -> TutorGenerationResponse:
        ...
