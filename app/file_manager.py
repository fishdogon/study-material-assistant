# 导入 Path，用来处理文件路径
from pathlib import Path

# 导入 UploadFile，这是 FastAPI 里处理上传文件的类型
from fastapi import UploadFile

from app.chunker import chunk_documents
from app.ingestion.parser_factory import ParserFactory
from app.material_metadata import delete_material_metadata, get_material_metadata


def resolve_material_labels(metadata: dict) -> dict:
    subject = metadata.get("subject", "") or metadata.get("suggested_subject", "")
    grade = metadata.get("grade", "") or metadata.get("suggested_grade", "")
    topic = metadata.get("topic", "") or metadata.get("suggested_topic", "")

    return {
        "subject": subject,
        "grade": grade,
        "topic": topic,
        "subject_source": "manual" if metadata.get("subject", "") else ("ai" if metadata.get("suggested_subject", "") else "empty"),
        "grade_source": "manual" if metadata.get("grade", "") else ("ai" if metadata.get("suggested_grade", "") else "empty"),
        "topic_source": "manual" if metadata.get("topic", "") else ("ai" if metadata.get("suggested_topic", "") else "empty"),
    }


def save_upload_file(file: UploadFile, save_dir: str = "data/raw") -> str:
    """
    保存上传的文件到指定目录。

    参数:
        file: FastAPI 接收到的上传文件对象
        save_dir: 文件保存目录，默认是 data/raw

    返回:
        保存后的文件路径（字符串）
    """

    # 把保存目录转成 Path 对象
    save_path = Path(save_dir)

    # 如果目录不存在，就自动创建
    save_path.mkdir(parents=True, exist_ok=True)

    # 拼出最终文件路径
    target_file = save_path / file.filename

    # 读取上传文件内容并写入本地
    with open(target_file, "wb") as f:
        f.write(file.file.read())

    # 返回文件路径字符串
    return str(target_file)


def list_materials(save_dir: str = "data/raw") -> list[dict]:
    """
    返回当前资料列表及其基础元信息。
    """

    save_path = Path(save_dir)
    if not save_path.exists():
        return []

    materials = []

    for file_path in sorted(save_path.iterdir(), key=lambda item: item.name.lower()):
        if not file_path.is_file():
            continue

        parser = ParserFactory.get_parser(file_path)
        if parser is None:
            continue

        parsed = parser.parse(file_path)
        if parsed is None:
            continue

        chunks = chunk_documents([parsed])
        metadata = get_material_metadata(file_path.name)
        labels = resolve_material_labels(metadata)

        materials.append({
            "id": file_path.name,
            "filename": file_path.name,
            "source_type": parsed.get("source_type", "unknown"),
            "parser_name": parsed.get("parser_name", "unknown"),
            "is_ocr": parsed.get("is_ocr", False),
            "chunk_count": len(chunks),
            "status": "indexed" if len(chunks) > 0 else "ready",
            "subject": labels["subject"],
            "grade": labels["grade"],
            "topic": labels["topic"],
            "subject_source": labels["subject_source"],
            "grade_source": labels["grade_source"],
            "topic_source": labels["topic_source"],
            "suggested_subject": metadata.get("suggested_subject", ""),
            "suggested_grade": metadata.get("suggested_grade", ""),
            "suggested_topic": metadata.get("suggested_topic", ""),
        })

    return materials


def filter_materials(
    source_names: list[str] | None = None,
    subject: str = "",
    grade: str = "",
    topic: str = "",
    save_dir: str = "data/raw"
) -> list[dict]:
    """
    根据文件名和元信息筛选资料。
    """

    materials = list_materials(save_dir=save_dir)

    if source_names:
        source_name_set = set(source_names)
        materials = [item for item in materials if item["filename"] in source_name_set]

    if subject.strip():
        materials = [item for item in materials if item.get("subject", "") == subject.strip()]

    if grade.strip():
        materials = [item for item in materials if item.get("grade", "") == grade.strip()]

    if topic.strip():
        materials = [item for item in materials if item.get("topic", "") == topic.strip()]

    return materials


def delete_material_file(filename: str, save_dir: str = "data/raw") -> bool:
    """
    删除指定资料文件。
    """

    target_file = Path(save_dir) / filename
    if not target_file.exists() or not target_file.is_file():
        return False

    target_file.unlink()
    delete_material_metadata(filename)
    return True
