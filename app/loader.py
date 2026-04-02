# 导入 Path，用来处理文件路径
from pathlib import Path

# 导入 PDF 加载函数
from app.pdf_loader import load_pdf_documents


def load_txt_documents(raw_dir: str = "data/raw") -> list[dict]:
    """
    读取 data/raw 目录下的所有 txt 文件。
    """

    raw_path = Path(raw_dir)
    documents = []

    for file_path in raw_path.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "content": text
        })

    return documents


def load_all_documents(raw_dir: str = "data/raw") -> list[dict]:
    """
    同时读取 txt 和 pdf 文档，并合并返回。
    """

    # 读取 txt
    txt_docs = load_txt_documents(raw_dir)

    # 读取 pdf
    pdf_docs = load_pdf_documents(raw_dir)

    # 合并两个列表
    return txt_docs + pdf_docs