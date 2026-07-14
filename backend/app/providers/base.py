from typing import Protocol

from backend.app.schemas import TutorGenerationRequest, TutorGenerationResponse


class ModelProviderError(Exception):
    def __init__(self, message: str, *, status: str = "error") -> None:
        super().__init__(message)
        self.status = status


class ModelProvider(Protocol):
    provider_name: str
    model_alias: str

    async def generate(self, request: TutorGenerationRequest) -> TutorGenerationResponse:
        ...
