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
    {
        "id": "data-labels",
        "title": "数据与标签",
        "order": 5,
        "prerequisites": ["classification"],
        "stage_goals": {
            Stage.lower_primary: "知道例子旁边的名字能帮助机器人学习。",
            Stage.upper_primary: "理解标签是告诉机器正确答案的小纸条。",
            Stage.middle_school: "理解样本、标签和监督学习的基本关系。",
            Stage.high_school: "理解特征矩阵与标签向量在监督学习中的作用。",
        },
        "intro": {
            Stage.lower_primary: "标签就像贴在盒子上的名字。",
            Stage.upper_primary: "数据是例子，标签是这个例子的正确类别。",
            Stage.middle_school: "带标签的数据能让模型比较预测和正确答案。",
            Stage.high_school: "监督学习用标注样本学习从输入特征到标签的映射。",
        },
    },
    {
        "id": "decision-tree",
        "title": "决策树直觉",
        "order": 6,
        "prerequisites": ["features"],
        "stage_goals": {
            Stage.lower_primary: "体验一步一步问问题来做决定。",
            Stage.upper_primary: "能用几个判断问题组成分类规则。",
            Stage.middle_school: "理解决策树按条件分支逐步分类。",
            Stage.high_school: "理解决策树通过特征划分形成可解释分类路径。",
        },
        "intro": {
            Stage.lower_primary: "决策树像猜谜游戏，一次问一个问题。",
            Stage.upper_primary: "决策树会沿着问题路线，把对象送到合适类别。",
            Stage.middle_school: "决策树把复杂判断拆成一连串条件分支。",
            Stage.high_school: "决策树在节点选择划分特征，叶子节点输出类别。",
        },
    },
    {
        "id": "accuracy",
        "title": "准确率",
        "order": 7,
        "prerequisites": ["train-test"],
        "stage_goals": {
            Stage.lower_primary: "知道答对越多，机器人越可靠。",
            Stage.upper_primary: "能用答对题数比较两个规则。",
            Stage.middle_school: "理解准确率是正确预测占总预测的比例。",
            Stage.high_school: "理解准确率的适用场景和类别不平衡时的局限。",
        },
        "intro": {
            Stage.lower_primary: "准确率就是机器人答对了多少次。",
            Stage.upper_primary: "准确率可以帮我们比较哪个分类规则更好。",
            Stage.middle_school: "准确率等于正确数量除以总数量。",
            Stage.high_school: "准确率是常用指标，但类别分布不均时需要结合其他指标。",
        },
    },
    {
        "id": "neural-network",
        "title": "神经网络直观原理",
        "order": 8,
        "prerequisites": ["features", "data-labels"],
        "stage_goals": {
            Stage.lower_primary: "知道很多小开关可以一起帮机器人判断。",
            Stage.upper_primary: "理解神经网络会把许多线索合在一起。",
            Stage.middle_school: "理解节点、连接和层的直观作用。",
            Stage.high_school: "理解神经网络通过层级变换提取表示并输出预测。",
        },
        "intro": {
            Stage.lower_primary: "神经网络像一队小助手，一起看线索。",
            Stage.upper_primary: "神经网络会把颜色、形状等线索合起来判断。",
            Stage.middle_school: "神经网络由很多节点和连接组成，会逐层处理信息。",
            Stage.high_school: "神经网络用多层非线性变换学习输入到输出的复杂映射。",
        },
    },
    {
        "id": "bias-safety",
        "title": "AI 偏差与安全",
        "order": 9,
        "prerequisites": ["data-labels"],
        "stage_goals": {
            Stage.lower_primary: "知道机器人也可能学错，要请老师检查。",
            Stage.upper_primary: "理解数据不全面会让 AI 判断不公平。",
            Stage.middle_school: "理解数据偏差会影响模型结果。",
            Stage.high_school: "理解数据偏差、隐私保护和模型安全的基本风险。",
        },
        "intro": {
            Stage.lower_primary: "如果例子不完整，机器人可能会猜错。",
            Stage.upper_primary: "AI 需要公平、丰富、合适的数据来学习。",
            Stage.middle_school: "训练数据有偏差时，模型可能把偏差学进去。",
            Stage.high_school: "AI 系统需要关注数据代表性、隐私和输出安全。",
        },
    },
    {
        "id": "project-practice",
        "title": "分类项目实践",
        "order": 10,
        "prerequisites": ["simple-classifier", "accuracy"],
        "stage_goals": {
            Stage.lower_primary: "完成一个帮助机器人分类的小任务。",
            Stage.upper_primary: "用规则完成一个生活分类项目。",
            Stage.middle_school: "设计数据、规则和测试流程完成小项目。",
            Stage.high_school: "用 Python 完成最小分类实验并解释结果。",
        },
        "intro": {
            Stage.lower_primary: "我们做一个小任务，帮机器人把东西分好。",
            Stage.upper_primary: "项目实践会把特征、规则和测试连起来。",
            Stage.middle_school: "项目要先定目标，再准备数据、测试并改进。",
            Stage.high_school: "分类项目需要数据处理、模型训练、评估和结果解释。",
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
