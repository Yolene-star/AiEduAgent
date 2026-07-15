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

        used_card_ids = request.retrieved_card_ids
        if not used_card_ids:
            return self._general_answer(request)

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

    def _general_answer(self, request: TutorGenerationRequest) -> TutorGenerationResponse:
        message = request.message
        if any(word in message for word in ("找到", "定位", "跟踪", "地址", "手机号")):
            answer = (
                "AI不能帮你偷偷定位别人或查别人的隐私，这样可能会伤害他人安全。"
                "如果你是真的想联系一位重要的人，可以先问家人、老师，或通过公开、正式、对方愿意的方式联系。"
                "AI能帮你整理一段礼貌的留言，也能解释为什么保护隐私很重要。"
            )
            check_question = "如果想联系别人，应该选择偷偷定位，还是请家人老师帮忙？"
        else:
            answer = (
                "这个问题不在当前U1知识卡里，但我可以先用通识方式回答：AI会根据你给出的文字、图片或规则寻找线索，"
                "再给出可能的建议。它不是魔法，也不能保证知道所有答案。遇到重要事情时，要让大人一起判断。"
                "回到本课，我们可以继续学AI怎样从图片和标签里学习。"
            )
            check_question = "AI给出的建议一定都是正确的吗？"

        return TutorGenerationResponse(
            answer=answer,
            check_question=check_question,
            used_card_ids=[],
            next_actions=["general_answer", "back_to_u1"],
            teaching_form="general_chat",
        )
