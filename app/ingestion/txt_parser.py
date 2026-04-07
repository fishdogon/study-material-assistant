from pathlib import Path
from app.ingestion.base_parser import BaseParser


class TxtParser(BaseParser):
    """
    txt 文件解析器。
    """

    def parse(self, file_path: Path) -> dict | None:
        try:
            text = file_path.read_text(encoding="utf-8").strip()

            if not text:
                return None

            return {
                "source": file_path.name,
                "content": text,
                "source_type": "txt",
                "parser_name": "TxtParser",
                "is_ocr": False
            }

        except Exception as e:
            print(f"[TxtParser] 解析失败: {file_path.name} -> {e}")
            return None