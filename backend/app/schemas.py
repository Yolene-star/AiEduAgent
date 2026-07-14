from typing import Literal

from pydantic import BaseModel, Field


Stage = Literal["lower_primary", "upper_primary", "middle_school", "high_school"]


class ChatRequest(BaseModel):
    stage: Stage
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    check_question: str
    used_card_ids: list[str]
    next_actions: list[str]


class TutorGenerationRequest(BaseModel):
    stage: Stage
    message: str = Field(min_length=1, max_length=500)
    request_id: str


class TutorGenerationResponse(BaseModel):
    answer: str = Field(min_length=1)
    check_question: str = Field(min_length=1)
    used_card_ids: list[str] = Field(min_length=1)
    next_actions: list[str] = Field(min_length=1)


def generation_to_chat_response(response: TutorGenerationResponse) -> ChatResponse:
    return ChatResponse(
        answer=response.answer,
        check_question=response.check_question,
        used_card_ids=response.used_card_ids,
        next_actions=response.next_actions,
    )
