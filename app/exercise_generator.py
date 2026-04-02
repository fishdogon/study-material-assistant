# 导入 OpenAI 兼容客户端
from openai import OpenAI

# 导入项目配置
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# 导入 re，用来清理模型输出中的多余内容
import re

# 导入 json，用来解析模型输出
import json


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


def generate_exercise(query: str, retrieved_chunks: list[dict]) -> dict:
    """
    根据用户需求 + 检索到的资料，生成结构化练习题结果。

    返回：
        一个 dict，而不是普通字符串
    """

    # 把检索到的资料内容拼接成上下文
    context = "\n\n".join(
        [
            f"[来源: {chunk['source']}]\n{chunk['content']}"
            for chunk in retrieved_chunks
        ]
    )

    # 系统提示词：强约束模型输出 JSON
    system_prompt = (
        "你是一名小学家教老师的出题助手。"
        "请严格基于给定资料内容生成练习题。"
        "不要输出任何额外解释，不要输出思考过程，不要使用 markdown 代码块。"
        "请直接输出 JSON。"
        "如果用户明确要求的是“和倍问题”，就不要混入差倍、和差、倍差等其他题型。"
        "如果资料里出现无关片段，要主动忽略它们。"
        "生成的题目必须自洽，答案必须能算通，不能出现你自己在答案里临时修题目的情况。"
        "尽量生成适合小学生，尤其三年级学生理解的题。"
        "每道题都要提供 explanation 字段，用于教学讲解。"
        "默认生成 3 道题。"
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
    user_prompt = f"用户需求：{query}\n\n资料内容：\n{context}"

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

    return parsed