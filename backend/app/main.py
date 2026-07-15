import logging
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.lesson_state import InvalidLessonTransition, default_event_for_state, transition_state
from backend.app.providers import ModelProviderError, get_model_provider
from backend.app.quiz import grade_quiz, list_quiz_questions, load_quizzes
from backend.app.knowledge import (
    filter_existing_card_ids,
    retrieve_cards,
    sources_for_card_ids,
    validate_knowledge_base,
)
from backend.app.stage_policy import get_stage_policy, validate_stage_output
from backend.app.schemas import (
    ChatRequest,
    ChatResponse,
    QuizQuestion,
    QuizSubmitRequest,
    QuizSubmitResponse,
    SourceLink,
    TutorGenerationRequest,
    generation_to_chat_response,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("aieduagent")
validate_knowledge_base()
load_quizzes()

app = FastAPI(title="AiEduAgent Backend", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type", "x-request-id"],
)


def fallback_chat_response() -> ChatResponse:
    used_card_ids = ["U1-C02", "U1-C04"]
    return ChatResponse(
        answer="模型暂时不可用，我先用固定知识卡帮你复习：机器会从带标签的图片中学习共同特点。",
        check_question="图片旁边写着‘小猫’，这个名字在训练中叫什么？",
        used_card_ids=used_card_ids,
        next_actions=["retry_later", "answer_check"],
        sources=sources_for_card_ids(used_card_ids),
        lesson_state="REMEDIATE",
        next_lesson_state="CHECK_UNDERSTANDING",
        teaching_form="remediate",
        stage_policy_label="fallback",
    )


def out_of_scope_response() -> ChatResponse:
    return ChatResponse(
        answer="模型暂时不可用，我不能可靠回答课外问题。你可以稍后再试，或先问像素、标签、训练数据、图像分类这些课内内容。",
        check_question="你想先了解“像素”“标签”还是“图像分类”？",
        used_card_ids=[],
        next_actions=["retry_later", "ask_u1_question"],
        sources=[],
        lesson_state="DIAGNOSE",
        next_lesson_state="EXPLAIN",
        teaching_form="boundary",
        stage_policy_label="U1 boundary",
    )


@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.exception(
            "request_id=%s path=%s status_code=500 duration_ms=%s",
            request_id,
            request.url.path,
            duration_ms,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
            headers={"x-request-id": request_id},
        )

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_id=%s path=%s status_code=%s duration_ms=%s",
        request_id,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    started_at = time.perf_counter()
    provider = None
    request_id = http_request.headers.get("x-request-id", str(uuid4()))
    policy = get_stage_policy(request.stage)
    lesson_event = request.lesson_event or default_event_for_state(request.lesson_state)
    try:
        next_lesson_state = transition_state(request.lesson_state, lesson_event)
    except InvalidLessonTransition:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Invalid lesson state transition",
                "lesson_state": request.lesson_state.value,
                "lesson_event": lesson_event.value,
            },
        )

    retrieved_cards = retrieve_cards(request.message)
    retrieved_card_ids = [card.id for card in retrieved_cards]
    canonical_claims = [
        f"{card.id} {claim}"
        for card in retrieved_cards
        for claim in card.canonical_claims
    ]
    generation_request = TutorGenerationRequest(
        stage=request.stage,
        message=request.message,
        request_id=request_id,
        retrieved_card_ids=retrieved_card_ids,
        canonical_claims=canonical_claims,
        lesson_state=request.lesson_state,
        next_lesson_state=next_lesson_state,
    )

    try:
        provider = get_model_provider()
        result = await provider.generate(generation_request)
        status = "ok"
        result.used_card_ids = filter_existing_card_ids(result.used_card_ids)
        if retrieved_card_ids and not result.used_card_ids:
            result.used_card_ids = retrieved_card_ids
        response = generation_to_chat_response(result)
        response.sources = [
            SourceLink.model_validate(source)
            for source in sources_for_card_ids(response.used_card_ids)
        ]
        response.lesson_state = request.lesson_state
        response.next_lesson_state = next_lesson_state
        response.stage_policy_label = policy.label
        validation = validate_stage_output(
            answer=response.answer,
            check_question=response.check_question,
            policy=policy,
        )
        response.format_warnings = list(validation.errors)
    except ModelProviderError as error:
        status = error.status
        logger.warning(
            "model_provider=%s model_alias=%s status=%s detail=%s request_id=%s",
            getattr(provider, "provider_name", "unknown"),
            getattr(provider, "model_alias", "unknown"),
            status,
            error.detail,
            request_id,
        )
        response = fallback_chat_response() if retrieved_card_ids else out_of_scope_response()

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "model_provider=%s model_alias=%s status=%s duration_ms=%s request_id=%s",
        getattr(provider, "provider_name", "unknown"),
        getattr(provider, "model_alias", "unknown"),
        status,
        duration_ms,
        request_id,
    )
    return response


@app.get("/api/v1/quizzes", response_model=list[QuizQuestion])
async def quizzes(stage: str | None = None):
    return list_quiz_questions(stage)


@app.post("/api/v1/quiz/{quiz_id}/submit", response_model=QuizSubmitResponse)
async def submit_quiz(quiz_id: str, request: QuizSubmitRequest):
    try:
        return grade_quiz(quiz_id, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Quiz not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
