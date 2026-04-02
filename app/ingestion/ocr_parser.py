# 导入 Path
from pathlib import Path

# 导入统一基类
from app.ingestion.base_parser import BaseParser


class OcrParser(BaseParser):
    """
    OCR 解析器（第一版占位实现）。

    这个类现在先不真正做 OCR，
    只负责占住“图片 / 扫描件资料以后该怎么接”的位置。

    后面如果你接 PaddleOCR，
    就主要改这个类里的 parse() 方法。
    """

    def parse(self, file_path: Path) -> dict | None:
        """
        解析图片 / 扫描类文件。

        当前版本：
        - 不真正识别
        - 只打印提示
        - 返回 None

        后面版本：
        - 调 OCR 模型
        - 提取文本
        - 返回统一格式
        """

        print(f"[OcrParser] 当前还未接入真正 OCR: {file_path.name}")

        # 现在先不处理，返回 None
        return None