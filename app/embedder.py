# 从 sentence_transformers 导入 SentenceTransformer
# 它的作用是把文本转成向量（embedding）
from sentence_transformers import SentenceTransformer


# 先定义一个全局变量，初始值是 None
# 这样做是为了避免每次调用时都重复加载模型
_model = None


def get_embedding_model():
    """
    获取 embedding 模型。

    这里做了一个简单的“懒加载”：
    - 第一次调用时加载模型
    - 后面再次调用时直接复用，不重复加载
    """

    global _model

    if _model is None:
        # 使用一个轻量、常见的 embedding 模型
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    把一组文本转成向量列表。

    参数:
        texts: 字符串列表，例如：
        ["平行线专题", "和倍问题专题"]

    返回:
        向量列表，每条文本对应一个向量
    """

    # 先获取模型
    model = get_embedding_model()

    # 调用模型编码文本
    # normalize_embeddings=True 表示把向量做归一化
    # 这样更适合后面做相似度检索
    embeddings = model.encode(texts, normalize_embeddings=True)

    # 把 numpy array 转成普通 Python list，方便后面交给 Chroma
    return embeddings.tolist()