# 导入 Path
from pathlib import Path

# 导入统一基类
from app.ingestion.base_parser import BaseParser


class TxtParser(BaseParser):
    """
    txt 文件解析器。
    """

    def parse(self, file_path: Path) -> dict | None:
        """
        读取 txt 文件内容，并返回统一格式。
        """

        try:
            # 读取 txt 文本
            text = file_path.read_text(encoding="utf-8").strip()

            # 如果内容为空，就返回 None
            if not text:
                return None

            # 返回统一格式
            return {
                "source": file_path.name,
                "content": text
            }

        except Exception as e:
            # 这里先简单打印错误，后面可以再升级成日志
            print(f"[TxtParser] 解析失败: {file_path.name} -> {e}")
            return None