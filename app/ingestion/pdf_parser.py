from pathlib import Path
from pypdf import PdfReader
from app.ingestion.base_parser import BaseParser


class PdfParser(BaseParser):
    """
    PDF 文件解析器。
    当前版本先只处理可直接提取文本的 PDF。
    """

    def parse(self, file_path: Path) -> dict | None:
        try:
            reader = PdfReader(str(file_path))
            full_text = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)

            combined_text = "\n".join(full_text).strip()

            if not combined_text:
                print(f"[PdfParser] 未提取到文本，后续可考虑 OCR: {file_path.name}")
                return None

            return {
                "source": file_path.name,
                "content": combined_text,
                "source_type": "pdf",
                "parser_name": "PdfParser",
                "is_ocr": False
            }

        except Exception as e:
            print(f"[PdfParser] 解析失败: {file_path.name} -> {e}")
            return None