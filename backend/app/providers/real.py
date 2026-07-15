import json
import logging
import time
from collections.abc import Mapping

import httpx
from pydantic import ValidationError

from backend.app.providers.base import ModelProviderError
from backend.app.schemas import TutorGenerationRequest, TutorGenerationResponse


logger = logging.getLogger("aieduagent")

REQUIRED_JSON_EXAMPLE = {
    "answer": "面向学生的回答",
    "check_question": "一个检查理解的问题？",
    "used_card_ids": ["U1-C04"],
    "next_actions": ["answer_check"],
    "teaching_form": "quick_quiz",
}


class RealModelProvider:
    provider_name = "real"

    def __init__(
        self,
        *,
        api_key: str,
        model_alias: str,
        base_url: str,
        timeout_seconds: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.model_alias = model_alias
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client = client

    async def generate(self, request: TutorGenerationRequest) -> TutorGenerationResponse:
        last_error: ModelProviderError | None = None

        for attempt in range(2):
            try:
                return await self._generate_once(request)
            except ModelProviderError as error:
                last_error = error
                if error.status != "rate_limited" or attempt == 1:
                    raise

        raise last_error or ModelProviderError("Model request failed")

    async def _generate_once(self, request: TutorGenerationRequest) -> TutorGenerationResponse:
        started_at = time.perf_counter()
        close_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self.timeout_seconds)

        try:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "authorization": f"Bearer {self.api_key}",
                    "content-type": "application/json",
                },
                json=self._build_payload(request),
            )
        except httpx.TimeoutException as exc:
            raise ModelProviderError("Model request timed out", status="timeout") from exc
        except httpx.HTTPError as exc:
            raise ModelProviderError("Model request failed", status="network_error") from exc
        finally:
            if close_client:
                await client.aclose()

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "model_provider=%s model_alias=%s status_code=%s duration_ms=%s request_id=%s",
            self.provider_name,
            self.model_alias,
            response.status_code,
            duration_ms,
            request.request_id,
        )

        if response.status_code == 429:
            raise ModelProviderError("Model rate limit", status="rate_limited", detail="http_429")
        if response.status_code >= 400:
            raise ModelProviderError(
                "Model HTTP error",
                status="http_error",
                detail=f"http_{response.status_code}:{response.text[:300]}",
            )

        return self._parse_response(response)

    def _build_payload(self, request: TutorGenerationRequest) -> dict[str, object]:
        claims = "\n".join(f"- {claim}" for claim in request.canonical_claims) or "- 无课内知识卡。"
        allowed_cards = ", ".join(request.retrieved_card_ids) or "无"
        scope_instruction = (
            "如果合法卡片ID为“无”，说明问题超出当前U1知识卡。"
            "请给出安全、适龄的通识回答，used_card_ids 必须返回空数组 []，不要编造来源。"
            "如果学生请求定位、跟踪、获取他人隐私或做危险事情，要温和拒绝，并给出求助家长、老师或正规渠道的替代建议。"
            "回答最后可以用一句话把问题自然引回人工智能课程。"
        )
        return {
            "model": self.model_alias,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是K12人工智能通识课教学助手。只输出JSON，字段必须为 "
                        "answer, check_question, used_card_ids, next_actions, teaching_form。"
                        "used_card_ids 只能从后端提供的合法卡片ID中选择，不能生成来源URL。"
                        f"{scope_instruction}"
                        "Return strict json only. Example json: "
                        f"{json.dumps(REQUIRED_JSON_EXAMPLE, ensure_ascii=False)}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"学段：{request.stage}\n"
                        f"当前状态：{request.lesson_state}\n"
                        f"下一状态：{request.next_lesson_state}\n"
                        f"问题：{request.message}\n"
                        f"合法卡片ID：{allowed_cards}\n"
                        f"事实边界：\n{claims}"
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 800,
            "temperature": 0.2,
        }

    def _parse_response(self, response: httpx.Response) -> TutorGenerationResponse:
        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ModelProviderError(
                "Model response shape is invalid",
                status="invalid_json",
                detail=f"shape:{response.text[:300]}",
            ) from exc

        if content is None or (isinstance(content, str) and not content.strip()):
            raise ModelProviderError("Model returned empty content", status="empty_content")

        try:
            data = json.loads(content) if isinstance(content, str) else content
        except json.JSONDecodeError as exc:
            raise ModelProviderError(
                "Model returned invalid JSON",
                status="invalid_json",
                detail=f"content:{str(content)[:300]}",
            ) from exc

        if not isinstance(data, Mapping):
            raise ModelProviderError("Model structured output is not an object", status="invalid_json")

        try:
            return TutorGenerationResponse.model_validate(data)
        except ValidationError as exc:
            raise ModelProviderError(
                "Model structured output validation failed",
                status="invalid_json",
                detail=f"validation:{exc.errors()}",
            ) from exc
