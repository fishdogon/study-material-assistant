# 导入 OpenAI 兼容客户端
from openai import OpenAI

# 导入配置
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# 导入 re，用来清理模型输出中的多余内容
import re


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


def generate_teaching_explanation(query: str, retrieved_chunks: list[dict]) -> str:
    """
    教学讲解模式：
    基于检索到的资料内容，生成更适合家教老师使用的讲解版本。
    """

    # 把检索到的片段拼成上下文
    context = "\n\n".join(
        [
            f"[来源: {chunk['source']}]\n{chunk['content']}"
            for chunk in retrieved_chunks
        ]
    )

    # 系统提示词：
    # 强调这是“教学讲解助手”，而不是普通问答
    system_prompt = (
        "你是一名有经验的小学家教老师助手。"
        "请严格基于给定资料内容，输出适合教学使用的讲解。"
        "回答时优先使用孩子容易理解的表达。"
        "如果资料不足，就明确说明，不要编造。"
        "回答时尽量包含以下内容："
        "1. 这道题或这个专题的核心思路；"
        "2. 适合怎么讲给学生；"
        "3. 常见易错点；"
        "4. 教学提醒。"
    )

    # 用户提示词：
    # 把用户问题和检索到的内容一起交给模型
    user_prompt = f"用户问题：{query}\n\n资料内容：\n{context}"

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