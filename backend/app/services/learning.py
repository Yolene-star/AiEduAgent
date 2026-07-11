from app.data.curriculum import list_knowledge_points
from app.services.store import SessionState


def update_mastery(session: SessionState, knowledge_point_id: str, correct: bool) -> int:
    current = session.mastery.get(knowledge_point_id, 0)
    delta = 18 if correct else -10
    updated = max(0, min(100, current + delta))
    session.mastery[knowledge_point_id] = updated
    return updated


def recommend_next(session: SessionState) -> dict[str, object]:
    points = list_knowledge_points(session.stage)
    weak = sorted(points, key=lambda item: session.mastery.get(str(item["id"]), 0))[0]
    score = session.mastery.get(str(weak["id"]), 0)
    if score < 60:
        return {
            "next_action": "review_with_animation",
            "knowledge_point_id": weak["id"],
            "reason": f"你在“{weak['title']}”的掌握度是 {score}，建议先看动画并完成一个小练习。",
            "estimated_minutes": 8,
        }
    next_point = points[min(len(points) - 1, 1)]
    return {
        "next_action": "continue_learning",
        "knowledge_point_id": next_point["id"],
        "reason": f"基础知识已经比较稳定，下一步可以学习“{next_point['title']}”。",
        "estimated_minutes": 10,
    }
