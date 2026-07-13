import logging
import time
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("aieduagent")

app = FastAPI(title="AiEduAgent Backend", version="0.2.0")

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


Stage = Literal["lower_primary", "upper_primary", "middle_school", "high_school"]


class ChatRequest(BaseModel):
    stage: Stage
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    check_question: str
    used_card_ids: list[str]
    next_actions: list[str]


class FakeModelProvider:
    def answer(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            answer="它会从许多带有名字的小猫图片中学习共同特点。",
            check_question="图片旁边写着‘小猫’，这个名字在训练中叫什么？",
            used_card_ids=["U1-C02", "U1-C04"],
            next_actions=["answer_check", "open_storybook"],
        )


fake_model_provider = FakeModelProvider()


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
async def chat(request: ChatRequest):
    return fake_model_provider.answer(request)
