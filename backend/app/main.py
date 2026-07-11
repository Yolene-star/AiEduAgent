from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.stages import STAGE_LABELS
from app.data.curriculum import COURSE, list_knowledge_points
from app.data.quizzes import questions_for, QUIZZES
from app.models import (
    ChatRequest,
    ChatResponse,
    Citation,
    CourseResponse,
    AnimationResponse,
    AnimationStep,
    CodeRunRequest,
    CodeRunResponse,
    HealthResponse,
    MasteryResponse,
    QuizGenerateRequest,
    QuizSubmitRequest,
    QuizSubmitResponse,
    RecommendationResponse,
    StudentSession,
    StudentSessionCreate,
    SystemInfo,
    TeacherAnalyticsResponse,
    TTSLoopbackRequest,
    TTSLoopbackResponse,
)
from app.services.dify import dify_client
from app.services.learning import recommend_next, update_mastery
from app.services.store import store
from app.services.tts import run_mock_loopback


settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)


@app.get("/api/system/info", response_model=SystemInfo)
def system_info() -> SystemInfo:
    return SystemInfo(
        name=settings.app_name,
        version=settings.app_version,
        ai_backend="dify" if dify_client.is_configured() else "local-fallback",
        tts_provider="mock-loopback",
    )


@app.post("/api/students/session", response_model=StudentSession)
def create_student_session(payload: StudentSessionCreate) -> StudentSession:
    session = store.create_session(stage=payload.stage, interest=payload.interest)
    label = STAGE_LABELS[payload.stage]
    return StudentSession(
        session_id=session.session_id,
        stage=session.stage,
        stage_label=label,
        welcome_message=f"你好，{label}同学。我们从“人工智能如何学会分类”开始。",
    )


@app.get("/api/courses", response_model=CourseResponse)
def courses(stage: str) -> CourseResponse:
    try:
        normalized_stage = next(item for item in STAGE_LABELS if item.value == stage)
    except StopIteration as exc:
        raise HTTPException(status_code=422, detail="invalid stage") from exc
    return CourseResponse(
        id=COURSE["id"],
        title=COURSE["title"],
        summary=COURSE["summary"],
        stage=normalized_stage,
        knowledge_points=list_knowledge_points(normalized_stage),
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        session = store.require_session(payload.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    answer, source = dify_client.generate_answer(session.stage, payload.message, payload.knowledge_point_id)
    store.add_message(session.session_id, "user", payload.message)
    store.add_message(session.session_id, "assistant", answer)
    return ChatResponse(
        answer=answer,
        stage=session.stage,
        knowledge_point_id=payload.knowledge_point_id,
        citations=[Citation(title="首期课程：人工智能如何学会分类", source="local-curriculum")],
        model_source=source,
    )


@app.post("/api/quizzes/generate")
def generate_quiz(payload: QuizGenerateRequest) -> dict[str, object]:
    try:
        session = store.require_session(payload.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    return {"questions": questions_for(session.stage, payload.knowledge_point_id)}


@app.post("/api/quizzes/submit", response_model=QuizSubmitResponse)
def submit_quiz(payload: QuizSubmitRequest) -> QuizSubmitResponse:
    try:
        session = store.require_session(payload.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc

    all_questions = [question for questions in QUIZZES.values() for question in questions]
    question = next((item for item in all_questions if item["id"] == payload.question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="question not found")

    correct = payload.answer == question["answer"]
    mastery = update_mastery(session, str(question["knowledge_point_id"]), correct)
    store.set_mastery(session.session_id, str(question["knowledge_point_id"]), mastery)
    store.record_quiz_attempt(session.session_id, payload.question_id, payload.answer, correct, mastery)
    feedback = "答对了，继续保持。" if correct else "这次还不稳，我们换个例子再练一次。"
    return QuizSubmitResponse(
        correct=correct,
        explanation=str(question["explanation"]),
        mastery=mastery,
        feedback=feedback,
    )


@app.get("/api/mastery", response_model=MasteryResponse)
def mastery(session_id: str) -> MasteryResponse:
    try:
        session = store.require_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    return MasteryResponse(session_id=session.session_id, mastery=session.mastery)


@app.get("/api/learning-path", response_model=RecommendationResponse)
def learning_path(session_id: str) -> RecommendationResponse:
    try:
        session = store.require_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    return RecommendationResponse(**recommend_next(session))


@app.get("/api/animations/classification", response_model=AnimationResponse)
def classification_animation() -> AnimationResponse:
    return AnimationResponse(
        id="classification-features",
        title="分类与特征动画",
        reference="Inspired by algorithm-visualizer state-sequence pattern; implemented from scratch.",
        steps=[
            AnimationStep(
                id="observe",
                title="观察对象",
                narration="先观察小动物，看看颜色、耳朵和尾巴这些线索。",
                highlighted_features=["颜色", "耳朵", "尾巴"],
                category="待判断",
            ),
            AnimationStep(
                id="choose-feature",
                title="选择特征",
                narration="选择真正有帮助的特征，不要用今天星期几这样的无关信息。",
                highlighted_features=["耳朵", "尾巴"],
                category="找线索",
            ),
            AnimationStep(
                id="classify",
                title="完成分类",
                narration="根据特征做判断，再用新例子检查这个规则稳不稳定。",
                highlighted_features=["规则", "新例子"],
                category="分类完成",
            ),
        ],
    )


@app.get("/api/teacher/analytics", response_model=TeacherAnalyticsResponse)
def teacher_analytics() -> TeacherAnalyticsResponse:
    weak: dict[str, int] = {}
    sessions = store.list_sessions()
    for session in sessions:
        for point_id, score in session.mastery.items():
            if score < 60:
                weak[point_id] = weak.get(point_id, 0) + 1
    return TeacherAnalyticsResponse(
        total_sessions=len(sessions),
        weak_knowledge_points=sorted(weak, key=weak.get, reverse=True),
        note="MVP uses SQLite-backed demo analytics. Replace with SQL aggregation when datasets grow.",
    )


@app.post("/api/code/run", response_model=CodeRunResponse)
def run_code(payload: CodeRunRequest) -> CodeRunResponse:
    try:
        store.require_session(payload.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    if payload.language != "python":
        raise HTTPException(status_code=422, detail="only python demo snippets are supported in MVP")
    if "import os" in payload.code or "open(" in payload.code:
        return CodeRunResponse(
            status="blocked",
            output="",
            feedback="这段代码包含文件或系统访问。MVP 会先阻止它，正式版将通过 Judge0 沙箱运行。",
            sandbox="mock-judge0",
        )
    return CodeRunResponse(
        status="ok",
        output="示例运行完成",
        feedback="MVP 暂不直接执行学生代码。正式版会接入 Judge0，并给出分级调试提示。",
        sandbox="mock-judge0",
    )


@app.post("/api/tts/loopback-test", response_model=TTSLoopbackResponse)
def tts_loopback(payload: TTSLoopbackRequest) -> TTSLoopbackResponse:
    return run_mock_loopback(payload.text, payload.stage)
