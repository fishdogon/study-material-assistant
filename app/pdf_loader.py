# 导入 Path，用来处理文件路径
from pathlib import Path

# 从 pypdf 导入 PdfReader
# 它的作用是读取 PDF 文件内容
from pypdf import PdfReader


def load_pdf_documents(raw_dir: str = "data/raw") -> list[dict]:
    """
    读取 data/raw 目录下的所有 PDF 文件，并提取文本内容。

    参数:
        raw_dir: 原始资料目录，默认是 data/raw

    返回:
        一个列表，每个元素都是一个字典，格式类似：
        {
            "source": "sample.pdf",
            "content": "提取出来的完整文本"
        }
    """

    # 把目录字符串转成 Path 对象
    raw_path = Path(raw_dir)

    # 用来存放所有读取到的 PDF 文档
    documents = []

    # 遍历目录下所有 pdf 文件
    for file_path in raw_path.glob("*.pdf"):
        # 创建 PDF 读取器
        reader = PdfReader(str(file_path))

        # 用来累积每一页的文本
        full_text = []

        # 遍历 PDF 的每一页
        for page in reader.pages:
            # extract_text() 会尝试提取这一页的文本
            # 有些 PDF 如果本质是图片扫描件，这里可能提不到文字
            page_text = page.extract_text()

            # 如果这一页成功提取到了文字，就加进去
            if page_text:
                full_text.append(page_text)

        # 把所有页拼成一个完整字符串
        combined_text = "\n".join(full_text).strip()

        # 如果这个 PDF 至少提取到了一些内容，就加入 documents
        if combined_text:
            documents.append({
                "source": file_path.name,
                "content": combined_text
            })

    return documents