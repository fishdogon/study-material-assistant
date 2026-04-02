# 导入 ABC 和 abstractmethod
# 这两个用于定义“抽象基类”
from abc import ABC, abstractmethod

# 导入 Path，方便处理文件路径
from pathlib import Path


class BaseParser(ABC):
    """
    所有文件解析器的抽象基类。

    它规定：以后不管是 txt、pdf、ocr、docx，
    只要是“资料解析器”，都尽量提供同样的 parse() 方法。
    """

    @abstractmethod
    def parse(self, file_path: Path) -> dict | None:
        """
        解析单个文件。

        参数:
            file_path: 文件路径

        返回:
            一个统一结构的字典，例如：
            {
                "source": "math_notes.txt",
                "content": "文件里的文本内容"
            }

        如果解析失败，可以返回 None。
        """
        pass