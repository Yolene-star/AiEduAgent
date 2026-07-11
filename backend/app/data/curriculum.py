from app.core.stages import Stage


COURSE = {
    "id": "ai-classification",
    "title": "人工智能如何学会分类",
    "summary": "用分类任务理解数据、特征、训练和测试。",
}


KNOWLEDGE_POINTS = [
    {
        "id": "classification",
        "title": "什么是分类",
        "order": 1,
        "prerequisites": [],
        "stage_goals": {
            Stage.lower_primary: "知道可以按相同特点把东西分成不同小组。",
            Stage.upper_primary: "理解分类需要观察特征，并按规则分组。",
            Stage.middle_school: "理解分类任务、类别和判定规则的关系。",
            Stage.high_school: "理解分类是监督学习中的基础任务，输入特征后预测类别。",
        },
        "intro": {
            Stage.lower_primary: "分类就像整理玩具，把相同特点的朋友放在一起。",
            Stage.upper_primary: "分类是根据颜色、形状、用途等特征，把对象放进合适类别。",
            Stage.middle_school: "分类是根据对象的特征，把它判断为某个类别的过程。",
            Stage.high_school: "分类模型学习样本特征与标签之间的关系，并对新样本预测标签。",
        },
    },
    {
        "id": "features",
        "title": "寻找关键特征",
        "order": 2,
        "prerequisites": ["classification"],
        "stage_goals": {
            Stage.lower_primary: "能说出颜色、耳朵、尾巴这样的特点。",
            Stage.upper_primary: "能选择更有帮助的分类特征。",
            Stage.middle_school: "理解不同特征会影响分类效果。",
            Stage.high_school: "理解特征工程会影响分类模型的泛化能力。",
        },
        "intro": {
            Stage.lower_primary: "特征就是我们观察到的小线索。",
            Stage.upper_primary: "特征是帮助我们判断类别的线索，比如颜色、大小、形状。",
            Stage.middle_school: "好特征能让分类规则更稳定，坏特征会带来误判。",
            Stage.high_school: "特征是模型输入变量，决定了模型可学习的信息边界。",
        },
    },
    {
        "id": "train-test",
        "title": "训练集与测试集",
        "order": 3,
        "prerequisites": ["classification", "features"],
        "stage_goals": {
            Stage.lower_primary: "知道机器人要先看例子，再试着回答新问题。",
            Stage.upper_primary: "理解练习例子和新挑战要分开。",
            Stage.middle_school: "理解训练数据和测试数据的作用不同。",
            Stage.high_school: "理解用训练集拟合模型，用测试集估计泛化表现。",
        },
        "intro": {
            Stage.lower_primary: "机器人先看很多例子，再试着认出新图片。",
            Stage.upper_primary: "训练集像练习题，测试集像新测验。",
            Stage.middle_school: "训练集用于学习规则，测试集用于检查规则是否可靠。",
            Stage.high_school: "训练集参与参数学习，测试集用于独立评估模型泛化性能。",
        },
    },
    {
        "id": "simple-classifier",
        "title": "简单分类器",
        "order": 4,
        "prerequisites": ["classification", "features", "train-test"],
        "stage_goals": {
            Stage.lower_primary: "体验用几条简单规则帮助机器人判断。",
            Stage.upper_primary: "能用规则做一个小分类器。",
            Stage.middle_school: "能比较不同规则的分类效果。",
            Stage.high_school: "能用 Python 写出最小分类实验并观察准确率。",
        },
        "intro": {
            Stage.lower_primary: "分类器像一个会按线索做决定的小助手。",
            Stage.upper_primary: "分类器会按照我们给的规则，把新对象放进类别。",
            Stage.middle_school: "分类器用特征和规则预测类别，可以通过测试结果改进。",
            Stage.high_school: "分类器是从特征空间到标签空间的映射，可用准确率等指标评估。",
        },
    },
]


def list_knowledge_points(stage: Stage) -> list[dict[str, object]]:
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "order": item["order"],
            "prerequisites": item["prerequisites"],
            "goal": item["stage_goals"][stage],
            "intro": item["intro"][stage],
        }
        for item in KNOWLEDGE_POINTS
    ]


def get_knowledge_point(point_id: str, stage: Stage) -> dict[str, object] | None:
    for item in list_knowledge_points(stage):
        if item["id"] == point_id:
            return item
    return None
