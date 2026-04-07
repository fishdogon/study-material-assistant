from pathlib import Path
import subprocess
import json

from app.ingestion.base_parser import BaseParser


class OcrParser(BaseParser):
    """
    OCR 解析器（通过独立 OCR 环境脚本调用）。
    """

    def parse(self, file_path: Path) -> dict | None:
        try:
            ocr_script = "/Users/long/Downloads/workSpace/ocr-test/run_ocr.py"
            ocr_python = "/Users/long/Downloads/workSpace/ocr-test/.venv/bin/python"

            result = subprocess.run(
                [ocr_python, ocr_script, str(file_path)],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            if not result.stdout.strip():
                print(f"[OcrParser] OCR 无输出: {file_path.name}")
                return None

            parsed = json.loads(result.stdout)

            if not parsed.get("success"):
                print(f"[OcrParser] OCR 失败: {file_path.name} -> {parsed.get('error')}")
                return None

            content = parsed.get("content", "").strip()

            if not content:
                print(f"[OcrParser] OCR 未识别到有效文本: {file_path.name}")
                return None

            return {
                "source": file_path.name,
                "content": content,
                "source_type": "image",
                "parser_name": "OcrParser",
                "is_ocr": True
            }

        except Exception as e:
            print(f"[OcrParser] 解析失败: {file_path.name} -> {e}")
            return None