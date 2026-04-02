# 导入 Path
from pathlib import Path

# 导入解析器工厂
from app.ingestion.parser_factory import ParserFactory


def load_all_documents(raw_dir: str = "data/raw") -> list[dict]:
    """
    统一加载 data/raw 下的所有支持文件。

    当前支持：
    - txt
    - pdf

    后面如果接入 OCR / docx，只需要继续扩展解析器工厂。
    """

    raw_path = Path(raw_dir)

    # 用来存放所有解析成功的文档
    documents = []

    # 遍历目录下所有文件
    for file_path in raw_path.iterdir():
        # 如果不是文件，就跳过
        if not file_path.is_file():
            continue

        # 让工厂根据文件类型返回解析器
        parser = ParserFactory.get_parser(file_path)

        # 如果当前格式不支持，就跳过
        if parser is None:
            print(f"[Loader] 跳过不支持的文件类型: {file_path.name}")
            continue

        # 调解析器解析文件
        doc = parser.parse(file_path)

        # 解析成功才加入 documents
        if doc is not None:
            documents.append(doc)

    return documents