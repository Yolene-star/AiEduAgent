import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.providers import ModelProviderError, get_model_provider
from backend.app.schemas import (
    ChatRequest,
    ChatResponse,
    TutorGenerationRequest,
    generation_to_chat_response,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("aieduagent")

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
    return ChatResponse(
        answer="模型暂时不可用，我先用固定知识卡帮你复习：机器会从带标签的图片中学习共同特点。",
        check_question="图片旁边写着‘小猫’，这个名字在训练中叫什么？",
        used_card_ids=["U1-C02", "U1-C04"],
        next_actions=["retry_later", "answer_check"],
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
    generation_request = TutorGenerationRequest(
        stage=request.stage,
        message=request.message,
        request_id=request_id,
    )

    try:
        provider = get_model_provider()
        result = await provider.generate(generation_request)
        status = "ok"
        response = generation_to_chat_response(result)
    except ModelProviderError as error:
        status = error.status
        logger.warning(
            "model_provider=%s model_alias=%s status=%s request_id=%s",
            getattr(provider, "provider_name", "unknown"),
            getattr(provider, "model_alias", "unknown"),
            status,
            request_id,
        )
        response = fallback_chat_response()

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
