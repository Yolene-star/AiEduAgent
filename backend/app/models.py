from pydantic import BaseModel, Field
from app.core.stages import Stage


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class SystemInfo(BaseModel):
    name: str
    version: str
    ai_backend: str
    tts_provider: str


class StudentSessionCreate(BaseModel):
    stage: Stage
    interest: str | None = None


class StudentSession(BaseModel):
    session_id: str
    stage: Stage
    stage_label: str
    welcome_message: str


class CourseResponse(BaseModel):
    id: str
    title: str
    summary: str
    stage: Stage
    knowledge_points: list[dict[str, object]]


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)
    knowledge_point_id: str = "classification"


class Citation(BaseModel):
    title: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    stage: Stage
    knowledge_point_id: str
    citations: list[Citation]
    model_source: str


class QuizGenerateRequest(BaseModel):
    session_id: str
    knowledge_point_id: str | None = None


class QuizSubmitRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str | None = None


class QuizSubmitResponse(BaseModel):
    correct: bool
    explanation: str
    mastery: int
    feedback: str


class MasteryResponse(BaseModel):
    session_id: str
    mastery: dict[str, int]


class RecommendationResponse(BaseModel):
    next_action: str
    knowledge_point_id: str
    reason: str
    estimated_minutes: int


class AnimationStep(BaseModel):
    id: str
    title: str
    narration: str
    highlighted_features: list[str]
    category: str


class AnimationResponse(BaseModel):
    id: str
    title: str
    reference: str
    steps: list[AnimationStep]


class TeacherAnalyticsResponse(BaseModel):
    total_sessions: int
    weak_knowledge_points: list[str]
    note: str


class CodeRunRequest(BaseModel):
    session_id: str
    language: str = "python"
    code: str = Field(min_length=1)


class CodeRunResponse(BaseModel):
    status: str
    output: str
    feedback: str
    sandbox: str


class TTSLoopbackRequest(BaseModel):
    text: str = Field(min_length=1)
    stage: Stage


class TTSLoopbackResponse(BaseModel):
    original_text: str
    loopback_text: str
    similarity: float
    stage_appropriate: bool
    safe: bool
    passed: bool
    notes: list[str]
