from dataclasses import dataclass
from typing import Literal

from backend.app.schemas import Stage


@dataclass(frozen=True)
class StagePolicy:
    stage: Stage
    label: str
    min_chars: int
    max_chars: int
    max_new_terms: int
    question_count: int
    example_types: tuple[str, ...]
    interaction_forms: tuple[str, ...]
    allows_formula: bool
    allows_code: bool


@dataclass(frozen=True)
class StageValidationResult:
    is_valid: bool
    errors: tuple[str, ...]


POLICIES: dict[Stage, StagePolicy] = {
    "lower_primary": StagePolicy(
        stage="lower_primary",
        label="小学低年级",
        min_chars=80,
        max_chars=150,
        max_new_terms=1,
        question_count=1,
        example_types=("story", "animal", "picture_choice"),
        interaction_forms=("storybook", "voice", "single_choice"),
        allows_formula=False,
        allows_code=False,
    ),
    "upper_primary": StagePolicy(
        stage="upper_primary",
        label="小学高年级",
        min_chars=150,
        max_chars=250,
        max_new_terms=2,
        question_count=1,
        example_types=("diagram", "game", "simple_steps"),
        interaction_forms=("drag_match", "quick_quiz"),
        allows_formula=False,
        allows_code=False,
    ),
    "middle_school": StagePolicy(
        stage="middle_school",
        label="初中",
        min_chars=250,
        max_chars=400,
        max_new_terms=5,
        question_count=1,
        example_types=("flow", "animation", "counterexample"),
        interaction_forms=("flow_animation", "pseudocode"),
        allows_formula=False,
        allows_code=True,
    ),
    "high_school": StagePolicy(
        stage="high_school",
        label="高中",
        min_chars=350,
        max_chars=600,
        max_new_terms=8,
        question_count=1,
        example_types=("algorithm", "code", "experiment", "ethics"),
        interaction_forms=("python_lab", "evaluation_task"),
        allows_formula=True,
        allows_code=True,
    ),
}

TRACKED_TERMS = (
    "像素",
    "标签",
    "训练数据",
    "图像分类",
    "训练集",
    "验证集",
    "测试集",
    "泛化",
    "特征",
    "分类器",
    "准确率",
    "算法",
)

FORMULA_MARKERS = ("=", "≈", "∑", ">", "<")
CODE_MARKERS = ("```", "def ", "for ", "while ", "print(", "return ")


def get_stage_policy(stage: Stage) -> StagePolicy:
    return POLICIES[stage]


def count_tracked_terms(text: str) -> int:
    return sum(1 for term in TRACKED_TERMS if term in text)


def count_questions(text: str) -> int:
    return text.count("?") + text.count("？")


def validate_stage_output(
    *,
    answer: str,
    check_question: str,
    policy: StagePolicy,
) -> StageValidationResult:
    errors: list[str] = []
    answer_length = len(answer)

    if answer_length < policy.min_chars:
        errors.append(f"answer_too_short:{answer_length}")
    if answer_length > policy.max_chars:
        errors.append(f"answer_too_long:{answer_length}")

    term_count = count_tracked_terms(answer)
    if term_count > policy.max_new_terms:
        errors.append(f"too_many_terms:{term_count}")

    if not policy.allows_formula and any(marker in answer for marker in FORMULA_MARKERS):
        errors.append("formula_not_allowed")

    if not policy.allows_code and any(marker in answer for marker in CODE_MARKERS):
        errors.append("code_not_allowed")

    question_count = count_questions(check_question)
    if question_count != policy.question_count:
        errors.append(f"wrong_question_count:{question_count}")

    return StageValidationResult(is_valid=not errors, errors=tuple(errors))


def render_stage_explanation(stage: Stage, concept_id: str) -> tuple[str, str, list[str]]:
    policy = get_stage_policy(stage)
    if stage == "lower_primary":
        return (
            "把电脑想成一位认真看相册的小老师。它先看很多已经写好名字的图片，比如这张是小猫、那张是小狗。看得多了，它会找共同样子，再遇到新图片时猜一猜。今天只记一个新词：标签，就是图片旁边的名字。",
            "图片旁边写着“小猫”，这个名字叫什么？",
            ["storybook", "answer_check"],
        )
    if stage == "upper_primary":
        return (
            "机器识别图片通常分三步。第一步，把图片变成许多颜色小点组成的数据。第二步，给图片配上正确名字，也就是标签，例如“小猫”。第三步，让模型反复看这些例子，学习哪些颜色、形状和边缘常常一起出现。新图片来了，它会根据学到的规律判断类别。这里的关键是：例子要够丰富，标签要尽量准确。你可以把它想成配对小游戏：图片和名字配得越认真，机器越容易学到稳定线索。",
            "在训练图片旁边写“小猫”，这个名字叫标签，对吗？",
            ["quick_quiz", "drag_match"],
        )
    if stage == "middle_school":
        return (
            "可以把图像分类看成一条流程：图片先被读成像素数据，再和标签组成训练样本，模型从样本中学习分类规律，最后对新图片输出类别。反例很重要：如果训练数据里几乎全是橘猫，模型可能把“橘色”误当成猫的关键特征，遇到黑猫就容易错。因果关系是，训练数据覆盖越窄，模型学到的规律越容易偏。伪代码可以写成：读取图片，提取特征，比较已学规律，输出类别。课堂动画可以把一张图片沿着这条流程移动，让你看到每一步的数据怎么变化，也能看到错误样本为什么需要回到数据环节检查。这样能把“为什么错”说清楚，而不是只看最后答案和分数哦。",
            "如果训练数据只有橘猫，模型遇到黑猫可能出什么问题？",
            ["flow_animation", "pseudocode"],
        )
    return (
        "从高中视角看，图像分类是一个监督学习任务：输入是图像张量，目标是预测类别标签。典型实验会先划分训练集、验证集和测试集；训练集用于更新模型参数，验证集用于选择方案，测试集用于估计未见样本上的效果。可以用 accuracy = 正确预测数 / 总样本数 做基础评估，但它不是万能指标；类别不平衡或数据偏差会让准确率显得过于乐观。实践中还要检查错误样本、混淆类别、数据来源和隐私边界。限制也要说清：模型并不真正理解猫，它是在已有数据分布上学习可计算的判别规律。项目实验可以让学生准备一个小型图片数据集，写 Python 读取目录、记录标签、划分数据，再比较不同划分下的结果波动。最后还要讨论伦理：图片是否获得授权，数据是否会暴露个人信息，错误分类会不会伤害真实用户。报告中应记录数据来源、划分比例和失败案例。",
        "为什么测试集不能在调参时反复偷看？",
        ["python_lab", "evaluation_task"],
    )
