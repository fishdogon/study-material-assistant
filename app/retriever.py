# 导入 Chroma 向量库实现
from app.vectorstores.chroma_store import ChromaVectorStore

# 导入 Qdrant 向量库实现
from app.vectorstores.qdrant_store import QdrantVectorStore


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


def keyword_score(query: str, content: str) -> int:
    """
    计算 query 和 content 的简单关键词命中分数。
    """
    score = 0

    for char in query:
        if char.strip() and char in content:
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


def search_relevant_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    检索最相关的 chunk。

    流程：
    1. 先让底层向量库召回 5 条
    2. 再按关键词命中数 + 语义排序值做简单重排
    3. 最后返回 top_k 条
    """

    retrieved = vector_store.search(query, top_k=5)

    for item in retrieved:
        item["keyword_score"] = keyword_score(query, item["content"])

    # 排序规则：
    # 1. 关键词命中高的优先
    # 2. 语义排序值更优的优先
    retrieved.sort(key=lambda x: (-x["keyword_score"], semantic_sort_value(x)))

    return retrieved[:top_k]