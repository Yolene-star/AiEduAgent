from difflib import SequenceMatcher
from app.core.stages import Stage, STAGE_RULES
from app.models import TTSLoopbackResponse


BLOCKED_TERMS = ["自伤", "隐私密码", "暴力伤害"]


def _similarity(a: str, b: str) -> float:
    return round(SequenceMatcher(None, a, b).ratio(), 3)


def run_mock_loopback(text: str, stage: Stage) -> TTSLoopbackResponse:
    loopback_text = text.strip()
    notes: list[str] = []
    safe = not any(term in loopback_text for term in BLOCKED_TERMS)
    if not safe:
        notes.append("包含不适合直接播报的风险词。")

    max_len = int(STAGE_RULES[stage]["max_sentence_length"])
    sentence_chunks = [chunk for chunk in loopback_text.replace("。", "。|").split("|") if chunk]
    stage_appropriate = all(len(chunk) <= max_len + 12 for chunk in sentence_chunks)
    if not stage_appropriate:
        notes.append("句子偏长，建议拆短后再播报。")

    similarity = _similarity(text.strip(), loopback_text)
    passed = bool(loopback_text) and safe and stage_appropriate and similarity >= 0.95
    if passed:
        notes.append("Mock TTS 回环通过。")

    return TTSLoopbackResponse(
        original_text=text,
        loopback_text=loopback_text,
        similarity=similarity,
        stage_appropriate=stage_appropriate,
        safe=safe,
        passed=passed,
        notes=notes,
    )
