# 导入 OpenAI 兼容客户端
from openai import OpenAI

# 导入项目配置
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
    清理模型返回中的多余内容，例如 <think> 标签、markdown 代码块等。
    """
    if not text:
        return ""

    # 去掉 <think> ... </think>
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)

    # 去掉 ```json 开头
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.I)

    # 去掉普通 ``` 开头
    text = re.sub(r"^```\s*", "", text.strip())

    # 去掉结尾的 ```
    text = re.sub(r"\s*```$", "", text.strip())

    return text.strip()


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    """
    普通资料问答模式：
    根据用户问题和检索到的资料片段，生成最终回答。

    参数:
        query: 用户问题
        retrieved_chunks: 检索到的相关资料片段列表

    返回:
        最终回答字符串
    """

    # 把检索到的片段拼成上下文
    context = "\n\n".join(
        [
            f"[来源: {chunk['source']}]\n{chunk['content']}"
            for chunk in retrieved_chunks
        ]
    )

    # 系统提示词：
    # 告诉模型现在是“资料问答模式”
    system_prompt = (
        "你是一个学习资料问答助手。"
        "请严格基于给定的检索内容回答问题。"
        "如果检索内容不足以回答，就明确说不知道，不要编造。"
        "回答尽量简洁、清晰。"
    )

    # 用户提示词：
    # 把问题和资料上下文一起给模型
    user_prompt = f"用户问题：{query}\n\n检索内容：\n{context}"

    # 调用模型
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # 取模型回答内容
    answer = response.choices[0].message.content

    # 清理后返回
    return clean_text(answer)