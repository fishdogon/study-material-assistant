from pathlib import Path
import json


METADATA_PATH = Path("data/material_metadata.json")
METADATA_FIELDS = ("subject", "grade", "topic")
SUGGESTED_METADATA_FIELDS = ("suggested_subject", "suggested_grade", "suggested_topic")


def _normalize_value(value) -> str:
    return str(value or "").strip()


def _normalize_entry(entry: dict | None) -> dict:
    current = entry or {}
    normalized = {}

    for field in (*METADATA_FIELDS, *SUGGESTED_METADATA_FIELDS):
        normalized[field] = _normalize_value(current.get(field, ""))

    return normalized


def _ensure_parent():
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_material_metadata() -> dict[str, dict]:
    if not METADATA_PATH.exists():
        return {}

    try:
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_material_metadata(metadata: dict[str, dict]):
    _ensure_parent()
    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_material_metadata(filename: str) -> dict:
    metadata = load_material_metadata()
    return _normalize_entry(metadata.get(filename, {}))


def update_material_metadata(filename: str, updates: dict) -> dict:
    metadata = load_material_metadata()
    current = _normalize_entry(metadata.get(filename, {}))

    for field in METADATA_FIELDS:
        if field in updates:
            current[field] = _normalize_value(updates.get(field))

    metadata[filename] = current
    save_material_metadata(metadata)
    return current


def update_material_ai_suggestions(filename: str, suggestions: dict) -> dict:
    metadata = load_material_metadata()
    current = _normalize_entry(metadata.get(filename, {}))

    for field in METADATA_FIELDS:
        suggested_field = f"suggested_{field}"
        current[suggested_field] = _normalize_value(suggestions.get(field))

    metadata[filename] = current
    save_material_metadata(metadata)
    return current


def delete_material_metadata(filename: str):
    metadata = load_material_metadata()
    if filename in metadata:
        metadata.pop(filename)
        save_material_metadata(metadata)
