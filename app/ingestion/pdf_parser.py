# 导入 Path
from pathlib import Path

# 导入 PdfReader，用于读取 PDF
from pypdf import PdfReader

# 导入统一基类
from app.ingestion.base_parser import BaseParser


class PdfParser(BaseParser):
    """
    PDF 文件解析器。

    这个版本先只处理“能直接提取文本”的 PDF。
    如果以后遇到扫描版 PDF，再接 OCR 解析器。
    """

    def parse(self, file_path: Path) -> dict | None:
        """
        读取 PDF 文件，并提取文本。
        """

        try:
            # 创建 PDF 读取器
            reader = PdfReader(str(file_path))

            # 用来收集所有页的文本
            full_text = []

            # 遍历 PDF 每一页
            for page in reader.pages:
                page_text = page.extract_text()

                # 如果这一页有内容，就加进去
                if page_text:
                    full_text.append(page_text)

            # 把所有页拼成一个大文本
            combined_text = "\n".join(full_text).strip()

            # 如果没提取到内容，就返回 None
            if not combined_text:
                return None

            # 返回统一格式
            return {
                "source": file_path.name,
                "content": combined_text
            }

        except Exception as e:
            print(f"[PdfParser] 解析失败: {file_path.name} -> {e}")
            return None