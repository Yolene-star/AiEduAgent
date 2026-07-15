from backend.app.providers.base import ModelProviderError
from backend.app.schemas import TutorGenerationRequest, TutorGenerationResponse
from backend.app.stage_policy import render_stage_explanation


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

        answer, check_question, next_actions = render_stage_explanation(
            request.stage,
            used_card_ids[0],
        )

        return TutorGenerationResponse(
            answer=answer,
            check_question=check_question,
            used_card_ids=used_card_ids[:3],
            next_actions=next_actions,
            teaching_form=next_actions[0],
        )
