# 导入 Path
from pathlib import Path

# 导入 txt 解析器
from app.ingestion.txt_parser import TxtParser

# 导入 pdf 解析器
from app.ingestion.pdf_parser import PdfParser

# 导入 OCR 解析器
from app.ingestion.ocr_parser import OcrParser


class ParserFactory:
    """
    解析器工厂。

    根据文件扩展名，返回对应的解析器实例。
    """

    @staticmethod
    def get_parser(file_path: Path):
        """
        根据文件路径后缀，返回对应解析器。
        """

        suffix = file_path.suffix.lower()

        # txt 文件
        if suffix == ".txt":
            return TxtParser()

        # pdf 文件
        if suffix == ".pdf":
            return PdfParser()

        # 图片文件：先走 OCR 解析器
        if suffix in {".png", ".jpg", ".jpeg"}:
            return OcrParser()

        # 当前不支持的类型
        return None