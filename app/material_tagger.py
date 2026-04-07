import json
import re
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from app.ingestion.parser_factory import ParserFactory


client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)


GRADE_PATTERNS = [
    "一年级",
    "二年级",
    "三年级",
    "四年级",
    "五年级",
    "六年级",
    "七年级",
    "八年级",
    "九年级",
    "高一",
    "高二",
    "高三",
]

SUBJECT_KEYWORDS = {
    "数学": ("数学", "算术", "几何", "方程", "口算", "应用题"),
    "语文": ("语文", "作文", "阅读理解", "古诗", "拼音", "写字"),
    "英语": ("英语", "English", "单词", "语法", "听力"),
    "物理": ("物理", "力学", "电学"),
    "化学": ("化学", "化学式", "酸碱"),
    "生物": ("生物", "细胞", "生态"),
}

TOPIC_HINTS = (
    "和倍问题",
    "差倍问题",
    "和差问题",
    "应用题",
    "口算",
    "计算",
    "几何",
    "阅读理解",
    "作文",
    "古诗",
)


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"^```\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    return text.strip()


def extract_json_text(text: str) -> str:
    text = clean_text(text)

    if text.startswith("{") and text.endswith("}"):
        return text

    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        return match.group(0)

    return text


def heuristic_tag_material(filename: str, content: str) -> dict:
    combined = f"{filename}\n{content[:1200]}"

    subject = ""
    for subject_name, keywords in SUBJECT_KEYWORDS.items():
        if any(keyword in combined for keyword in keywords):
            subject = subject_name
            break

    grade = ""
    for grade_name in GRADE_PATTERNS:
        if grade_name in combined:
            grade = grade_name
            break

    topic = ""
    for topic_name in TOPIC_HINTS:
        if topic_name in combined:
            topic = topic_name
            break

    return {
        "subject": subject,
        "grade": grade,
        "topic": topic,
    }


def parse_material_content(file_path: Path) -> dict | None:
    parser = ParserFactory.get_parser(file_path)
    if parser is None:
        return None

    return parser.parse(file_path)


def infer_material_metadata(file_path: Path) -> dict:
    parsed = parse_material_content(file_path)
    if parsed is None:
        return {
            "subject": "",
            "grade": "",
            "topic": "",
        }

    content = parsed.get("content", "").strip()
    heuristic_result = heuristic_tag_material(file_path.name, content)
    excerpt = content[:1800]

    system_prompt = (
        "你是一个学习资料标签助手。"
        "请根据资料文件名和资料内容，给出最可能的学科、年级、专题。"
        "只输出 JSON，不要输出任何额外说明。"
        "JSON 结构固定为："
        "{\"subject\":\"\",\"grade\":\"\",\"topic\":\"\"}"
        "如果无法判断，就返回空字符串。"
        "学科尽量使用常见中文学科名，例如数学、语文、英语。"
        "年级尽量使用中文表达，例如二年级、三年级。"
        "专题尽量简洁，例如和倍问题、应用题、阅读理解。"
    )
    user_prompt = (
        f"文件名：{file_path.name}\n"
        f"来源类型：{parsed.get('source_type', 'unknown')}\n"
        f"资料内容摘录：\n{excerpt}\n\n"
        f"你也可以参考这份规则猜测结果：{json.dumps(heuristic_result, ensure_ascii=False)}"
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_text = response.choices[0].message.content
        result = json.loads(extract_json_text(raw_text))

        return {
            "subject": str(result.get("subject", "")).strip() or heuristic_result["subject"],
            "grade": str(result.get("grade", "")).strip() or heuristic_result["grade"],
            "topic": str(result.get("topic", "")).strip() or heuristic_result["topic"],
        }
    except Exception:
        return heuristic_result
