# 导入 chromadb，用来做本地向量库
import chromadb

# 导入 Path，用来处理本地路径
from pathlib import Path

# 导入 embedding 函数
from app.embedder import embed_texts


# 本地向量库存放路径
DB_PATH = str(Path("storage/chroma_db"))


def build_vector_store(chunks: list[dict]):
    """
    根据 chunk 列表建立本地向量库。
    """

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="study_materials")

    if chunks:
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [{"source": chunk["source"]} for chunk in chunks]
        embeddings = embed_texts(documents)

        # 先清空旧数据，避免重复添加
        try:
            existing = collection.get()
            if existing and existing.get("ids"):
                collection.delete(ids=existing["ids"])
        except Exception:
            pass

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    return collection


def keyword_score(query: str, content: str) -> int:
    """
    计算 query 和 content 的简单关键词命中分数。

    这里先用一个非常朴素的办法：
    遍历 query 里的每个字符，只要这个字符也出现在 content 里，就加分。

    注意：
    这不是最优算法，但很适合你当前这个学习阶段，简单、直观、容易理解。
    """
    score = 0

    for char in query:
        # 跳过空格和换行这类无意义字符
        if char.strip() and char in content:
            score += 1

    return score


def search_relevant_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    根据用户问题，检索最相关的 chunk。

    检索策略：
    1. 先用向量检索召回一批结果
    2. 再按“关键词命中数 + 向量距离”做一次简单重排
    """

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="study_materials")

    # 先把用户问题转成向量
    query_embedding = embed_texts([query])[0]

    # 先召回稍微多一点结果，例如 5 个
    # 这样后面重排才有意义
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    retrieved = []

    for i in range(len(results["ids"][0])):
        content = results["documents"][0][i]

        item = {
            "id": results["ids"][0][i],
            "content": content,
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i],
            "keyword_score": keyword_score(query, content)
        }

        retrieved.append(item)

    # 排序规则：
    # 1. 关键词命中数越高越靠前
    # 2. 如果关键词分数相同，则 distance 越小越靠前
    retrieved.sort(key=lambda x: (-x["keyword_score"], x["distance"]))

    # 最后只返回 top_k 条
    return retrieved[:top_k]