# 导入 OpenAI 兼容客户端
from openai import OpenAI

# 导入项目配置
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# 导入 re，用来清理模型输出中的多余内容
import re

# 导入 json，用来解析模型输出
import json
from app.prompt_utils import (
    build_prompt_context,
    build_exercise_layering_instruction,
    build_exercise_stage_labels,
    build_topic_guard_instruction,
    extract_expected_exercise_count,
    infer_exercise_difficulty,
)


# 创建模型客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)


def clean_text(text: str) -> str:
    """
    清理模型输出中的 <think> 标签、markdown 代码块等多余内容。
    """
    if not text:
        return ""

    # 去掉思考标签
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)

    # 去掉 markdown 代码块包裹
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"^```\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    return text.strip()


def extract_json_text(text: str) -> str:
    """
    从模型返回内容里尽量提取 JSON 主体。

    为什么要做这个？
    因为模型有时不会老老实实只返回 JSON，
    可能会在前后加说明文字。
    """

    # 先做基础清洗
    text = clean_text(text)

    # 如果本身就是以 { 开头、以 } 结尾，那直接返回
    if text.startswith("{") and text.endswith("}"):
        return text

    # 尝试用正则提取最外层 JSON 对象
    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        return match.group(0)

    # 如果提取不到，就原样返回，后面让 json.loads 去报错
    return text


def validate_exercise_result(data: dict) -> bool:
    """
    校验练习题生成结果是否符合预期结构。
    """

    if "topic" not in data or not isinstance(data["topic"], str):
        return False

    if "grade" not in data or not isinstance(data["grade"], str):
        return False

    if "exercises" not in data or not isinstance(data["exercises"], list):
        return False

    for item in data["exercises"]:
        if not isinstance(item, dict):
            return False

        required_fields = ["title", "problem", "intent", "hint", "answer", "explanation"]

        for field in required_fields:
            if field not in item or not isinstance(item[field], str):
                return False

    return True


def post_process_exercises(data: dict, expected_count: int, difficulty: str) -> dict:
    exercises = data.get("exercises", [])
    if not isinstance(exercises, list):
        return data

    stage_labels = build_exercise_stage_labels(len(exercises), difficulty)

    for index, item in enumerate(exercises):
        if not isinstance(item, dict):
            continue

        stage_label = stage_labels[index] if index < len(stage_labels) else f"练习 {index + 1}"
        title = (item.get("title") or "").strip()
        intent = (item.get("intent") or "").strip()
        hint = (item.get("hint") or "").strip()

        if not title:
            item["title"] = f"{stage_label} {index + 1}"
        elif stage_label not in title:
            item["title"] = f"{stage_label}｜{title}"

        if intent and stage_label not in intent:
            item["intent"] = f"{stage_label}：{intent}"

        if hint and stage_label not in hint and difficulty in {"标准", "提高"}:
            item["hint"] = f"{stage_label}提示：{hint}"

    data["exercises"] = exercises
    return data


def generate_exercise(
    query: str,
    retrieved_chunks: list[dict],
    style: str = "2",
    difficulty: str = "",
    expected_count: int = 0,
) -> dict:
    """
    根据用户需求 + 检索到的资料，生成结构化练习题结果。

    返回：
        一个 dict，而不是普通字符串
    """

    context = build_prompt_context(retrieved_chunks)
    expected_count = expected_count or extract_expected_exercise_count(query)
    difficulty = difficulty or infer_exercise_difficulty(query)
    topic_guard_instruction = build_topic_guard_instruction(query)
    layering_instruction = build_exercise_layering_instruction(expected_count, difficulty)

    style_instruction = {
        "1": "本次只需要题目训练感，answer 和 explanation 字段可以简短但必须保留字符串，供系统结构校验使用。",
        "2": "本次要给出题目和清晰可算通的参考答案，explanation 字段可以简短。",
        "3": "本次要给出题目、参考答案和适合家长或老师讲解的 explanation。explanation 必须具体，不要只写一句话。",
    }.get(style, "本次要给出题目和清晰可算通的参考答案。")

    difficulty_instruction = {
        "基础": "题目难度以基础巩固为主，数字设置不要过大，步骤不要过绕。",
        "标准": "题目难度保持常规练习水平，兼顾理解和计算。",
        "提高": "题目可以略有提升，但仍要保持小学阶段能理解，不能脱离当前专题。",
    }[difficulty]

    # 系统提示词：强约束模型输出 JSON
    system_prompt = (
        "你是一名小学家教老师的出题助手。"
        "请严格基于给定资料内容生成练习题。"
        "不要输出任何额外解释，不要输出思考过程，不要使用 markdown 代码块。"
        "请直接输出 JSON。"
        f"{topic_guard_instruction}"
        "如果资料里出现无关片段，要主动忽略它们。"
        "生成的题目必须自洽，答案必须能算通，不能出现你自己在答案里临时修题目的情况。"
        "尽量生成适合小学生，尤其三年级学生理解的题。"
        "请先从资料中识别主专题、合适年级，再围绕该专题稳定出题。"
        f"本次目标题量是 {expected_count} 道。"
        f"本次目标难度是：{difficulty}。"
        f"{difficulty_instruction}"
        f"{layering_instruction}"
        "每道题都要提供 explanation 字段，用于教学讲解。"
        f"{style_instruction}"
        "输出 JSON 结构如下："
        "{"
        "\"topic\": \"题目主题\","
        "\"grade\": \"适合年级\","
        "\"exercises\": ["
        "{"
        "\"title\": \"小标题\","
        "\"problem\": \"题目内容\","
        "\"intent\": \"出题意图\","
        "\"hint\": \"提示\","
        "\"answer\": \"参考答案\","
        "\"explanation\": \"给老师的简短讲解思路\""
        "}"
        "]"
        "}"
    )

    # 用户提示词
    user_prompt = (
        f"用户需求：{query}\n"
        f"输出风格编号：{style}\n\n"
        f"请生成 {expected_count} 道题。\n"
        f"请把难度控制在“{difficulty}”水平。\n"
        "请保持题型纯度，不要混入相近但不同的数学专题。\n"
        "如果适合，请让题目从基础到变式再到略提升，形成自然层次。\n\n"
        f"资料内容：\n{context}"
    )

    # 调模型
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # 1. 先取出模型原始输出
    raw_text = response.choices[0].message.content

    # 2. 再从原始输出里提取 JSON 文本
    result_text = extract_json_text(raw_text)

    # 3. 解析 JSON
    parsed = json.loads(result_text)

    # 4. 校验结构
    if not validate_exercise_result(parsed):
        raise ValueError("练习题生成结果结构不合法，请检查模型输出。")

    if isinstance(parsed.get("exercises"), list):
        parsed["exercises"] = parsed["exercises"][:expected_count]

    parsed = post_process_exercises(parsed, expected_count=expected_count, difficulty=difficulty)
    parsed["difficulty"] = difficulty
    parsed["requested_count"] = expected_count

    return parsed
