# 导入 Chroma 向量库实现
from app.vectorstores.chroma_store import ChromaVectorStore

# 导入 Qdrant 向量库实现
from app.vectorstores.qdrant_store import QdrantVectorStore
from app.prompt_utils import extract_query_terms, normalize_text


# 当前选择的向量库类型
VECTOR_STORE_TYPE = "qdrant"


def get_vector_store():
    """
    根据配置返回不同的向量库实例。
    """
    if VECTOR_STORE_TYPE == "qdrant":
        return QdrantVectorStore()

    return ChromaVectorStore()


# 创建全局向量库实例
vector_store = get_vector_store()


def build_vector_store(chunks: list[dict]):
    """
    建立向量索引。
    """
    vector_store.build(chunks)


def clear_vector_store():
    """
    清空当前向量索引。
    """
    vector_store.clear()


def keyword_score(query: str, content: str) -> int:
    """
    计算 query 和 content 的关键词命中分数。
    优先奖励完整短语命中，其次奖励 query 中较长词片段命中。
    """
    normalized_query = normalize_text(query)
    normalized_content = normalize_text(content)

    if not normalized_query or not normalized_content:
        return 0

    score = 0

    if normalized_query in normalized_content:
        score += min(len(normalized_query), 18) * 3

    terms = extract_query_terms(query)
    for term in terms:
        if term in normalized_content:
            score += len(term) * 3

    unique_chars = {char for char in normalized_query if char.strip()}
    for char in unique_chars:
        if char in normalized_content:
            score += 1

    return score


def semantic_sort_value(item: dict) -> float:
    """
    给不同向量库返回的结果统一一个可排序值。

    - 对 Chroma：distance 越小越好，所以直接返回 distance
    - 对 Qdrant：score 越大越好，但我们目前把它暂存进了 distance 字段
      所以这里取负数，转成“越小越好”的统一排序值
    """
    value = item["distance"]

    if VECTOR_STORE_TYPE == "qdrant":
        return -value

    return value


def search_relevant_chunks(
    query: str,
    top_k: int = 3,
    source_names: list[str] | None = None,
    exclude_ocr: bool = False
) -> list[dict]:
    """
    检索最相关的 chunk。

    流程：
    1. 先让底层向量库召回 5 条
    2. 再按关键词命中数 + 语义排序值做简单重排
    3. 最后返回 top_k 条
    """

    if source_names is not None and len(source_names) == 0:
        return []

    candidate_k = 16 if source_names is not None or exclude_ocr else 8
    retrieved = vector_store.search(query, top_k=candidate_k)

    if source_names is not None:
        source_name_set = set(source_names)
        retrieved = [item for item in retrieved if item.get("source") in source_name_set]

    if exclude_ocr:
        retrieved = [item for item in retrieved if not item.get("is_ocr", False)]

    for item in retrieved:
        item["keyword_score"] = keyword_score(query, item["content"])

    # 排序规则：
    # 1. 关键词命中高的优先
    # 2. 语义排序值更优的优先
    retrieved.sort(key=lambda x: (-x["keyword_score"], semantic_sort_value(x)))

    return retrieved[:top_k]
