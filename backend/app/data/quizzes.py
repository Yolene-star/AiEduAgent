from app.core.stages import Stage


QUIZZES = {
    Stage.lower_primary: [
        {
            "id": "lp-classification-1",
            "knowledge_point_id": "classification",
            "type": "single_choice",
            "prompt": "把苹果、香蕉、梨放在一起，是按什么分类？",
            "options": ["水果", "交通工具", "衣服"],
            "answer": "水果",
            "explanation": "它们都是可以吃的水果。",
        }
    ],
    Stage.upper_primary: [
        {
            "id": "up-features-1",
            "knowledge_point_id": "features",
            "type": "single_choice",
            "prompt": "判断猫和狗时，下面哪个更像有用特征？",
            "options": ["耳朵形状", "今天星期几", "教室门牌号"],
            "answer": "耳朵形状",
            "explanation": "耳朵形状和动物外观有关，更可能帮助分类。",
        }
    ],
    Stage.middle_school: [
        {
            "id": "ms-train-test-1",
            "knowledge_point_id": "train-test",
            "type": "single_choice",
            "prompt": "为什么测试集不应该参与训练？",
            "options": ["否则评估会不公平", "因为测试集没有数据", "因为模型不能读取文本"],
            "answer": "否则评估会不公平",
            "explanation": "测试集要模拟新问题，参与训练会让成绩失真。",
        }
    ],
    Stage.high_school: [
        {
            "id": "hs-classifier-1",
            "knowledge_point_id": "simple-classifier",
            "type": "single_choice",
            "prompt": "分类模型的输入通常是什么？",
            "options": ["特征向量", "网页标题", "随机颜色"],
            "answer": "特征向量",
            "explanation": "分类模型根据特征向量预测类别标签。",
        }
    ],
}


def questions_for(stage: Stage, knowledge_point_id: str | None = None) -> list[dict[str, object]]:
    questions = QUIZZES[stage]
    if knowledge_point_id:
        filtered = [q for q in questions if q["knowledge_point_id"] == knowledge_point_id]
        return filtered or questions
    return questions
