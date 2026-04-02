# 导入 chromadb，用来做本地向量库
import chromadb

# 导入 Path，用来处理本地路径
from pathlib import Path

# 导入 embedding 函数
from app.embedder import embed_texts

# 导入基类
from app.vectorstores.base import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    """
    基于 Chroma 的向量库实现。

    它遵循 BaseVectorStore 规定的接口：
    - build()
    - search()
    """

    def __init__(self, db_path: str = "storage/chroma_db", collection_name: str = "study_materials"):
        """
        初始化 Chroma 向量库实例。

        参数:
            db_path: 本地 Chroma 数据库存储路径
            collection_name: collection 名称
        """
        self.db_path = str(Path(db_path))
        self.collection_name = collection_name

    def _get_collection(self):
        """
        获取或创建 collection。

        这是一个内部辅助函数，避免重复写相同代码。
        """
        client = chromadb.PersistentClient(path=self.db_path)
        collection = client.get_or_create_collection(name=self.collection_name)
        return collection

    def build(self, chunks: list[dict]):
        """
        根据 chunk 列表建立向量索引。
        """

        collection = self._get_collection()

        if chunks:
            # 提取 id、文本内容、metadata
            ids = [chunk["id"] for chunk in chunks]
            documents = [chunk["content"] for chunk in chunks]
            metadatas = [{"source": chunk["source"]} for chunk in chunks]

            # 生成 embeddings
            embeddings = embed_texts(documents)

            # 为了避免重复 add，先尝试清空旧数据
            try:
                existing = collection.get()
                if existing and existing.get("ids"):
                    collection.delete(ids=existing["ids"])
            except Exception:
                pass

            # 写入 Chroma
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        根据 query 做向量检索。

        注意：
        这里默认先召回 top_k=5，
        后面 retriever.py 还可以继续做二次重排。
        """

        collection = self._get_collection()

        # 把 query 也转成向量
        query_embedding = embed_texts([query])[0]

        # 调 Chroma query
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # 整理返回结果
        retrieved = []

        for i in range(len(results["ids"][0])):
            retrieved.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "distance": results["distances"][0][i]
            })

        return retrieved