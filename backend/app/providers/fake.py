from backend.app.providers.base import ModelProviderError
from backend.app.schemas import TutorGenerationRequest, TutorGenerationResponse


class FakeModelProvider:
    provider_name = "fake"
    model_alias = "fixed-stage-2-answer"

    def __init__(self, failure_mode: str | None = None) -> None:
        self.failure_mode = failure_mode

    async def generate(self, request: TutorGenerationRequest) -> TutorGenerationResponse:
        if self.failure_mode == "timeout":
            raise ModelProviderError("Fake timeout injection", status="timeout")
        if self.failure_mode == "rate_limit":
            raise ModelProviderError("Fake rate limit injection", status="rate_limited")
        if self.failure_mode == "invalid_json":
            raise ModelProviderError("Fake invalid JSON injection", status="invalid_json")

        used_card_ids = request.retrieved_card_ids or ["U1-C02", "U1-C04"]
        if not used_card_ids:
            used_card_ids = ["U1-C02", "U1-C04"]

        return TutorGenerationResponse(
            answer="它会从许多带有名字的小猫图片中学习共同特点。",
            check_question="图片旁边写着‘小猫’，这个名字在训练中叫什么？",
            used_card_ids=used_card_ids[:3],
            next_actions=["answer_check", "open_storybook"],
        )
