from app.core.config import get_settings
from app.core.stages import Stage, STAGE_LABELS, STAGE_RULES
from app.data.curriculum import get_knowledge_point


class DifyClient:
    """Small Dify adapter.

    MVP tests use the local fallback so development does not require network or API keys.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.dify_api_key)

    def generate_answer(self, stage: Stage, message: str, knowledge_point_id: str) -> tuple[str, str]:
        if not self.is_configured():
            return self._fallback_answer(stage, message, knowledge_point_id), "local-fallback"
        # Network calls are intentionally isolated here. The implementation can be
        # swapped for httpx when API credentials are available.
        return self._fallback_answer(stage, message, knowledge_point_id), "dify-adapter-fallback"

    def _fallback_answer(self, stage: Stage, message: str, knowledge_point_id: str) -> str:
        point = get_knowledge_point(knowledge_point_id, stage)
        title = point["title"] if point else "分类"
        intro = point["intro"] if point else "分类是把对象放进合适类别。"
        label = STAGE_LABELS[stage]
        style = STAGE_RULES[stage]["style"]

        if stage == Stage.lower_primary:
            return f"{label}讲法：{intro} 你可以先找一个小线索，再试着分一分。"
        if stage == Stage.upper_primary:
            return f"{label}讲法：{intro} 回答“{message}”时，我们先找特征，再说明分类规则。"
        if stage == Stage.middle_school:
            return f"{label}讲法：围绕“{title}”，{intro} 可以用例子、规则和测试结果来检查理解。"
        return f"{label}讲法：围绕“{title}”，{intro} 对问题“{message}”，建议从特征、标签、训练数据和泛化评估四步分析。"


dify_client = DifyClient()
