# 导入 ABC 和 abstractmethod
# ABC = Abstract Base Class，表示抽象基类
# abstractmethod 表示“子类必须实现的方法”
from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    """
    向量库抽象基类。

    这个类不直接干活，它的作用是：
    规定所有向量库实现都应该提供哪些方法。

    以后无论你用 Chroma、Qdrant，还是别的向量库，
    都尽量遵守这套接口。
    """

    @abstractmethod
    def build(self, chunks: list[dict]):
        """
        根据 chunk 列表建立向量索引。

        参数:
            chunks: 文本块列表
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        根据用户问题做检索。

        参数:
            query: 用户问题
            top_k: 返回前几个结果

        返回:
            检索结果列表
        """
        pass

    @abstractmethod
    def clear(self):
        """
        清空当前向量库中的资料索引。
        """
        pass
