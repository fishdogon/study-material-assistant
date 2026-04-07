# 导入 uuid，用来生成点 id
import uuid

# 导入 Qdrant 客户端
from qdrant_client import QdrantClient

# 导入 Qdrant 里定义向量点的数据结构
from qdrant_client.models import Distance, VectorParams, PointStruct

# 导入 embedding 函数
from app.embedder import embed_texts

# 导入基类
from app.vectorstores.base import BaseVectorStore


class QdrantVectorStore(BaseVectorStore):
    """
    基于 Qdrant 的向量库实现。

    它和 ChromaVectorStore 一样，也遵循 BaseVectorStore 的统一接口：
    - build()
    - search()

    这样以后切库时，上层代码基本不用改。
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "study_materials"
    ):
        """
        初始化 Qdrant 向量库实例。

        参数:
            host: Qdrant 服务地址
            port: Qdrant 服务端口
            collection_name: collection 名称
        """

        self.host = host
        self.port = port
        self.collection_name = collection_name

        # 创建 Qdrant 客户端
        self.client = QdrantClient(host=self.host, port=self.port)

    def _recreate_collection(self, vector_size: int):
        """
        重建 collection。

        为什么要这样做？
        因为第一次建库时，Qdrant 需要知道向量维度。
        """

        # 如果 collection 已存在，就删除
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except Exception:
            pass

        # 重新创建 collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,          # 向量维度
                distance=Distance.COSINE   # 余弦相似度
            )
        )

    def build(self, chunks: list[dict]):
        """
        根据 chunk 列表建立 Qdrant 向量索引。
        """

        if not chunks:
            return

        # 提取文本内容
        documents = [chunk["content"] for chunk in chunks]

        # 做 embedding
        embeddings = embed_texts(documents)

        # 根据第一条 embedding 的长度，确定向量维度
        vector_size = len(embeddings[0])

        # 重建 collection
        self._recreate_collection(vector_size=vector_size)

        # 组装 points
        points = []

        for chunk, vector in zip(chunks, embeddings):
            points.append(
                PointStruct(
                    # Qdrant 的 id 可以是 int 或 str
                    # 这里用 uuid 保证唯一
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "chunk_id": chunk["id"],
                        "source": chunk["source"],
                        "content": chunk["content"],
                        "source_type": chunk.get("source_type", "unknown"),
                        "parser_name": chunk.get("parser_name", "unknown"),
                        "is_ocr": chunk.get("is_ocr", False)
                    }
                )
            )

        # 写入 Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def clear(self):
        """
        清空 collection。
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except Exception:
            pass

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        根据 query 做向量检索。
        """

        # 把 query 转成向量
        query_vector = embed_texts([query])[0]

        # 新版 qdrant-client 推荐用 query_points
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )

        # 兼容返回结构：points 在 results.points 里
        retrieved = []

        for item in results.points:
            retrieved.append({
                "id": item.payload["chunk_id"],
                "content": item.payload["content"],
                "source": item.payload["source"],
                "source_type": item.payload.get("source_type", "unknown"),
                "parser_name": item.payload.get("parser_name", "unknown"),
                "is_ocr": item.payload.get("is_ocr", False),
                "distance": item.score
            })

        return retrieved
