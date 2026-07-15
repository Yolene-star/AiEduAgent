import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.providers import ModelProviderError, get_model_provider
from backend.app.schemas import TutorGenerationRequest


async def main() -> int:
    provider_name = os.getenv("MODEL_PROVIDER", "fake")
    model = os.getenv("LLM_MODEL", "")
    base_url = os.getenv("LLM_BASE_URL", "")
    has_key = bool(os.getenv("LLM_API_KEY"))

    print(f"MODEL_PROVIDER={provider_name}")
    print(f"LLM_MODEL={model or '<empty>'}")
    print(f"LLM_BASE_URL={base_url or '<empty>'}")
    print(f"LLM_API_KEY_SET={has_key}")

    request = TutorGenerationRequest(
        stage="lower_primary",
        message="AI怎么认识小猫？",
        request_id="manual-provider-check",
        retrieved_card_ids=["U1-C04", "U1-C02"],
        canonical_claims=[
            "U1-C04 图像分类的目标是给整张图片预测一个或多个类别。",
            "U1-C02 在监督学习中，标签是模型要学习预测的答案或目标值。",
        ],
    )

    try:
        provider = get_model_provider()
        response = await provider.generate(request)
    except ModelProviderError as error:
        print(f"RESULT=failed status={error.status} detail={error.detail}")
        return 1

    print("RESULT=ok")
    print(f"USED_CARD_IDS={response.used_card_ids}")
    print(f"TEACHING_FORM={response.teaching_form}")
    print(f"ANSWER_PREVIEW={response.answer[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
