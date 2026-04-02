# 从 langchain_text_splitters 导入递归字符切分器
# 它的作用是把一大段文本切成多个较小的文本块
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    把读取到的原始文档切分成多个 chunk（文本块）。

    参数:
        documents: 原始文档列表，格式类似：
        [
            {
                "source": "math_notes.txt",
                "content": "平行线专题......"
            }
        ]

    返回:
        切分后的 chunk 列表，格式类似：
        [
            {
                "id": "math_notes.txt_0",
                "source": "math_notes.txt",
                "content": "第一块内容"
            },
            {
                "id": "math_notes.txt_1",
                "source": "math_notes.txt",
                "content": "第二块内容"
            }
        ]
    """

    # 创建一个文本切分器
    # chunk_size=120 表示每一块大约 120 个字符
    # chunk_overlap=20 表示相邻两块之间保留 20 个字符重叠
    # 这样做可以减少“一个知识点被从中间切断”的问题
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=120,
        chunk_overlap=20
    )

    # 用来存放所有切分后的 chunk
    chunks = []

    # 遍历每一份原始文档
    for doc in documents:
        # 对当前文档内容进行切分
        split_texts = splitter.split_text(doc["content"])

        # 遍历切出来的每一个小块
        for idx, chunk_text in enumerate(split_texts):
            # 把每一个 chunk 组织成统一结构
            chunks.append({
                "id": f"{doc['source']}_{idx}",  # 唯一 id，例如 math_notes.txt_0
                "source": doc["source"],        # 来源文件名
                "content": chunk_text           # 当前这一小块文本
            })

    # 返回所有 chunk
    return chunks