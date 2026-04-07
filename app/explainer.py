# 导入 OpenAI 兼容客户端
from openai import OpenAI

# 导入配置
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# 导入 re，用来清理模型输出中的多余内容
import re
from app.prompt_utils import (
    build_prompt_context,
    build_topic_guard_instruction,
    infer_explanation_depth,
    infer_teaching_mode,
)


# 创建模型客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)


def clean_text(text: str) -> str:
    """
    清理模型输出中的多余内容，例如 <think> 标签或 markdown 代码块。
    """
    if not text:
        return ""

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"^```\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    return text.strip()


def build_teaching_outline(teaching_mode: str) -> str:
    if teaching_mode == "teacher":
        return (
            "请严格按以下 Markdown 结构输出，标题顺序不要变：\n"
            "## 这份资料主要在讲什么\n"
            "用 2 到 4 句话概括专题、目标和适合年级。\n\n"
            "## 核心思路\n"
            "用 2 到 4 个要点说明这类题/这个专题最重要的思考方法。\n\n"
            "## 课堂讲解顺序\n"
            "按步骤写出老师可以怎么展开讲。\n\n"
            "## 可以直接对孩子说的话\n"
            "给出 2 到 4 句能直接对孩子说的解释话术。\n\n"
            "## 常见易错点\n"
            "列出最容易错的地方，并说明为什么会错。\n\n"
            "## 教学提醒\n"
            "补充提问方式、板书提醒或课堂组织建议。"
        )

    return (
        "请严格按以下 Markdown 结构输出，标题顺序不要变：\n"
        "## 这份资料主要在讲什么\n"
        "用 2 到 4 句话概括专题、目标和适合年级。\n\n"
        "## 核心思路\n"
        "用 2 到 4 个要点说明这类题/这个专题最重要的思考方法。\n\n"
        "## 分步骤讲解\n"
        "把讲解拆成 2 到 4 个步骤，每一步都尽量简洁清楚。\n\n"
        "## 可以直接对孩子说的话\n"
        "给出 2 到 4 句能直接对孩子说的解释话术。\n\n"
        "## 常见易错点\n"
        "列出最容易错的地方，并说明为什么会错。\n\n"
        "## 辅导提醒\n"
        "补充家长/辅导者在带孩子时要注意什么。"
    )


def generate_teaching_explanation(
    query: str,
    retrieved_chunks: list[dict],
    teaching_mode: str = "",
    explanation_depth: str = "",
) -> str:
    """
    教学讲解模式：
    基于检索到的资料内容，生成更适合家教老师使用的讲解版本。
    """

    context = build_prompt_context(retrieved_chunks)
    teaching_mode = teaching_mode or infer_teaching_mode(query)
    explanation_depth = explanation_depth or infer_explanation_depth(query)
    topic_guard_instruction = build_topic_guard_instruction(query)

    mode_instruction = {
        "teacher": "本次更偏老师备课/课堂讲解场景，请多给讲解顺序、提问方式和教学提醒。",
        "parent": "本次更偏家长辅导场景，请多用家长能直接转述给孩子的话术。",
        "general": "本次保持通用辅导风格，既清楚又便于转述。",
    }[teaching_mode]

    depth_instruction = {
        "detailed": "本次请写得更完整一些，步骤展开，不要只给结论。",
        "brief": "本次请控制篇幅，重点清楚，不要展开过长。",
        "standard": "本次篇幅适中，重点和提醒要完整。",
    }[explanation_depth]
    outline_instruction = build_teaching_outline(teaching_mode)

    # 系统提示词：
    # 强调这是“教学讲解助手”，而不是普通问答
    system_prompt = (
        "你是一名非常有经验的小学数学家教老师助手。"
        "你的任务不是普通问答，而是把资料转成可以直接拿去辅导孩子的讲解稿。"
        "请严格基于给定资料内容回答，忽略无关片段，不要编造。"
        "默认面向家长辅导场景，语言要自然、通俗、可转述。"
        "如果用户没有明确年级，也要根据资料内容尽量选择适合低龄学生理解的表达。"
        f"{topic_guard_instruction}"
        f"{mode_instruction}"
        f"{depth_instruction}"
        "请使用 Markdown 输出。"
        "如果是数学题型讲解，请尽量把思路拆成 2 到 4 个清晰步骤。"
        "每个一级部分都要真的填写内容，不要只写标题。"
        "如果某一部分信息不足，也要在该部分明确写出“根据当前资料暂时无法进一步展开”。"
        "如果资料不足，请明确指出“根据当前资料还不能完全判断”的部分。"
        "不要输出与你身份无关的寒暄。"
    )

    # 用户提示词：
    # 把用户问题和检索到的内容一起交给模型
    user_prompt = (
        f"用户问题：{query}\n\n"
        "请先判断资料中最相关的专题与年级，再组织讲解。\n\n"
        f"{outline_instruction}\n\n"
        f"资料内容：\n{context}"
    )

    # 调模型生成讲解
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # 清洗输出并返回
    answer = response.choices[0].message.content
    return clean_text(answer)
