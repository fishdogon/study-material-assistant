import re


MATH_TOPICS = [
    "和倍问题",
    "差倍问题",
    "和差问题",
    "倍差问题",
    "归一问题",
    "植树问题",
    "鸡兔同笼",
    "平行线",
    "分数",
    "百分数",
    "小数",
    "应用题",
    "行程问题",
    "工程问题",
    "温度",
]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").strip().lower())


def extract_query_terms(query: str) -> list[str]:
    cleaned = re.sub(r"[，。！？；：、,.!?;:()\[\]{}\"'“”‘’\s]+", " ", query or "")
    terms = [item.strip().lower() for item in cleaned.split(" ") if len(item.strip()) >= 2]

    # 去重并保持顺序
    unique_terms: list[str] = []
    for term in terms:
        if term not in unique_terms:
            unique_terms.append(term)
    return unique_terms


def extract_expected_exercise_count(query: str, default: int = 3) -> int:
    query = query or ""

    match = re.search(r"([0-9]+)\s*道", query)
    if match:
        return max(1, min(int(match.group(1)), 8))

    cn_map = {
        "一": 1,
        "两": 2,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
    }
    match = re.search(r"([一二两三四五六七八])\s*道", query)
    if match:
        return cn_map.get(match.group(1), default)

    if "几道" in query:
        return default

    return default


def infer_exercise_difficulty(query: str) -> str:
    normalized = normalize_text(query)

    if any(keyword in normalized for keyword in ["拔高", "提高", "进阶", "难一点", "综合"]):
        return "提高"

    if any(keyword in normalized for keyword in ["基础", "简单", "入门", "容易"]):
        return "基础"

    return "标准"


def infer_teaching_mode(query: str) -> str:
    normalized = normalize_text(query)

    if any(keyword in normalized for keyword in ["老师", "课堂", "备课", "板书", "教学设计"]):
        return "teacher"

    if any(keyword in normalized for keyword in ["孩子", "家长", "听懂", "转述", "在家"]):
        return "parent"

    return "general"


def infer_explanation_depth(query: str) -> str:
    normalized = normalize_text(query)

    if any(keyword in normalized for keyword in ["详细", "展开", "完整", "一步一步", "具体"]):
        return "detailed"

    if any(keyword in normalized for keyword in ["简要", "简单", "简短", "快速"]):
        return "brief"

    return "standard"


def infer_primary_math_topic(query: str) -> str:
    normalized = normalize_text(query)

    for topic in MATH_TOPICS:
        if normalize_text(topic) in normalized:
            return topic

    return ""


def build_topic_guard_instruction(query: str) -> str:
    topic = infer_primary_math_topic(query)
    if not topic:
        return "如果资料中存在多个近似专题，请优先选择与用户问题最一致的专题，不要混讲。"

    confusing_pairs = {
        "和倍问题": "不要混入差倍问题、和差问题、倍差问题。",
        "差倍问题": "不要混入和倍问题、和差问题、倍差问题。",
        "和差问题": "不要混入和倍问题、差倍问题。",
        "倍差问题": "不要混入和倍问题、差倍问题。",
        "平行线": "不要混入垂线、角度计算等无关专题。",
        "分数": "不要混入小数或百分数计算，除非资料明确涉及。",
        "百分数": "不要混入普通分数和小数专题，除非资料明确涉及。",
    }

    extra = confusing_pairs.get(topic, "不要混入相近但不同的数学专题。")
    return f"本次主专题应视为“{topic}”。{extra}"


def build_exercise_layering_instruction(expected_count: int, difficulty: str) -> str:
    if expected_count <= 1:
        return "只生成 1 道题，直接给出最贴合当前专题的代表题。"

    if difficulty == "基础":
        return f"这 {expected_count} 道题都应偏基础巩固，数字设置平稳，步骤清楚。"

    if difficulty == "提高":
        if expected_count >= 3:
            return (
                f"这 {expected_count} 道题应保持同专题，建议前 1-2 道作为铺垫，后面逐步提高，"
                "但不要超过当前年级认知范围。"
            )
        return f"这 {expected_count} 道题可以略有提高，但仍要保持同专题和可讲解性。"

    if expected_count >= 3:
        return (
            f"这 {expected_count} 道题建议做分层：前面先基础巩固，中间做同类变式，最后一题略作提升。"
            "标题、意图和提示要体现这种层次。"
        )

    return f"这 {expected_count} 道题保持同专题与同层次，难度自然递进。"


def build_exercise_stage_labels(expected_count: int, difficulty: str) -> list[str]:
    if expected_count <= 1:
        return ["代表题"]

    if difficulty == "基础":
        return ["基础巩固"] * expected_count

    if difficulty == "提高":
        if expected_count == 2:
            return ["铺垫题", "提高题"]
        if expected_count == 3:
            return ["铺垫题", "变式题", "提高题"]
        return ["铺垫题"] + ["变式题"] * max(expected_count - 2, 1) + ["提高题"]

    if expected_count == 2:
        return ["基础巩固", "同类变式"]
    if expected_count == 3:
        return ["基础巩固", "同类变式", "略提高"]

    return ["基础巩固"] + ["同类变式"] * max(expected_count - 2, 1) + ["略提高"]


def format_chunk_for_prompt(chunk: dict) -> str:
    source = chunk.get("source", "unknown")
    source_type = chunk.get("source_type", "unknown")
    is_ocr = "是" if chunk.get("is_ocr", False) else "否"
    parser_name = chunk.get("parser_name", "unknown")
    keyword_score = chunk.get("keyword_score", 0)
    distance = chunk.get("distance", 0)
    content = chunk.get("content", "")

    return (
        f"[来源文件] {source}\n"
        f"[来源类型] {source_type}\n"
        f"[是否 OCR] {is_ocr}\n"
        f"[解析器] {parser_name}\n"
        f"[关键词命中分] {keyword_score}\n"
        f"[相似度排序值] {distance}\n"
        f"[内容]\n{content}"
    )


def build_prompt_context(retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        return "暂无可用资料内容。"

    return "\n\n---\n\n".join(
        [format_chunk_for_prompt(chunk) for chunk in retrieved_chunks]
    )
