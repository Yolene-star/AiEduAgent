from typing import Literal

from pydantic import BaseModel, Field

from backend.app.lesson_state import LessonEvent, LessonState


Stage = Literal["lower_primary", "upper_primary", "middle_school", "high_school"]
ResourceType = Literal["link", "document", "ppt", "video", "image", "knowledge_card", "quiz"]
ResourceStatus = Literal["draft", "pending_review"]
AnimationVisual = Literal["image-card", "pixel-grid", "feature-lines", "score-bars", "label-badge"]
AnimationControl = Literal["play", "pause", "restart", "previous", "next"]


class ChatRequest(BaseModel):
    stage: Stage
    message: str = Field(min_length=1, max_length=500)
    lesson_state: LessonState = LessonState.WELCOME
    lesson_event: LessonEvent | None = None


class SourceLink(BaseModel):
    card_id: str
    title: str
    url: str


class CourseResourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    resource_type: ResourceType
    stage: Stage | None = None
    unit: str = Field(default="U1", min_length=1, max_length=40)
    topic: str = Field(min_length=1, max_length=120)
    source_url: str | None = Field(default=None, max_length=500)
    license: str = Field(default="unknown", min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    card_ids: list[str] = Field(default_factory=list)
    created_by: str = Field(default="demo-teacher", min_length=1, max_length=80)


class CourseResourceResponse(CourseResourceCreate):
    id: str
    status: ResourceStatus
    created_at: str


class AnimationStep(BaseModel):
    id: str = Field(min_length=1, max_length=60)
    title: str = Field(min_length=1, max_length=80)
    caption: str = Field(min_length=1, max_length=240)
    visual: AnimationVisual


class AnimationSpec(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    concept_id: str = Field(pattern=r"^U1-C\d{2}$")
    template: Literal["image_classification_process"]
    version: int = Field(ge=1)
    subtitle: str = Field(min_length=1, max_length=240)
    steps: list[AnimationStep] = Field(min_length=5, max_length=5)
    allowed_controls: list[AnimationControl] = Field(min_length=1)
    license: str = Field(min_length=1)


class StorybookPage(BaseModel):
    page: int = Field(ge=1, le=6)
    title: str = Field(min_length=1, max_length=80)
    image: str = Field(min_length=1, max_length=200)
    alt: str = Field(min_length=1, max_length=200)
    narration: str = Field(min_length=1, max_length=240)
    dialogue: str = Field(min_length=1, max_length=240)
    question: str = Field(min_length=1, max_length=160)


class StorybookSpec(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    stage: Stage
    concept_id: str = Field(pattern=r"^U1-C\d{2}$")
    version: int = Field(ge=1)
    recommended_by_default: bool
    pages: list[StorybookPage] = Field(min_length=6, max_length=6)
    license: str = Field(min_length=1)


QuizType = Literal["multiple_choice", "true_false", "ordering"]


class QuizOption(BaseModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class QuizQuestion(BaseModel):
    id: str = Field(min_length=1)
    stage: Stage
    card_id: str = Field(pattern=r"^U1-C\d{2}$")
    quiz_type: QuizType
    prompt: str = Field(min_length=1)
    options: list[QuizOption] = Field(default_factory=list)
    items: list[QuizOption] = Field(default_factory=list)
    review_card_id: str = Field(pattern=r"^U1-C\d{2}$")


class QuizSubmitRequest(BaseModel):
    student_id: str = Field(default="demo-student", min_length=1, max_length=80)
    answer: str | bool | list[str]
    hints_used: int = Field(default=0, ge=0, le=10)
    elapsed_ms: int = Field(default=0, ge=0)
    idempotency_key: str = Field(min_length=8, max_length=120)


class QuizSubmitResponse(BaseModel):
    question_id: str
    correct: bool
    explanation: str
    error_type: str
    review_card_id: str
    next_actions: list[str]
    already_recorded: bool = False


class ChatResponse(BaseModel):
    answer: str
    check_question: str
    used_card_ids: list[str]
    next_actions: list[str]
    sources: list[SourceLink] = Field(default_factory=list)
    lesson_state: LessonState = LessonState.EXPLAIN
    next_lesson_state: LessonState = LessonState.CHECK_UNDERSTANDING
    teaching_form: str = "quick_quiz"
    stage_policy_label: str = ""
    format_warnings: list[str] = Field(default_factory=list)


class TutorGenerationRequest(BaseModel):
    stage: Stage
    message: str = Field(min_length=1, max_length=500)
    request_id: str
    retrieved_card_ids: list[str] = []
    canonical_claims: list[str] = []
    lesson_state: LessonState = LessonState.EXPLAIN
    next_lesson_state: LessonState = LessonState.CHECK_UNDERSTANDING


class TutorGenerationResponse(BaseModel):
    answer: str = Field(min_length=1)
    check_question: str = Field(min_length=1)
    used_card_ids: list[str]
    next_actions: list[str] = Field(min_length=1)
    teaching_form: str = Field(min_length=1)


def generation_to_chat_response(response: TutorGenerationResponse) -> ChatResponse:
    return ChatResponse(
        answer=response.answer,
        check_question=response.check_question,
        used_card_ids=response.used_card_ids,
        next_actions=response.next_actions,
        teaching_form=response.teaching_form,
    )
