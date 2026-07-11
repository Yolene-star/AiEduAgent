from enum import Enum


class Stage(str, Enum):
    lower_primary = "lower_primary"
    upper_primary = "upper_primary"
    middle_school = "middle_school"
    high_school = "high_school"


STAGE_LABELS: dict[Stage, str] = {
    Stage.lower_primary: "小学低年级",
    Stage.upper_primary: "小学高年级",
    Stage.middle_school: "初中",
    Stage.high_school: "高中",
}


STAGE_RULES: dict[Stage, dict[str, object]] = {
    Stage.lower_primary: {
        "max_sentence_length": 24,
        "style": "短句、故事化、少术语、用生活比喻",
        "activity": "图片选择和角色故事",
    },
    Stage.upper_primary: {
        "max_sentence_length": 36,
        "style": "图文解释、生活案例、少量关键词",
        "activity": "拖拽分类和互动绘本",
    },
    Stage.middle_school: {
        "max_sentence_length": 48,
        "style": "概念清晰、流程图、探究式提问",
        "activity": "动画讲解和小实验",
    },
    Stage.high_school: {
        "max_sentence_length": 72,
        "style": "术语准确、算法直觉、代码实践",
        "activity": "Python 实验和项目任务",
    },
}
