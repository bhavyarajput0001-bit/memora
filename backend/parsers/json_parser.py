"""JSON parser — preserves structured data."""
import json

from backend.utils import generate_id, file_hash


def parse_json_file(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse a JSON file. Returns structured data + text representation."""
    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1", errors="replace")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {
            "id": doc_id,
            "filename": filename,
            "source_type": "json",
            "file_hash": fhash,
            "title": filename,
            "full_text": text,
            "pages": [{"page": 1, "text": text}],
            "metadata": {"parse_error": True},
            "extraction_method": "json-parse-failed",
        }

    # Build a readable text representation
    full_text = json.dumps(data, indent=2, ensure_ascii=False)

    metadata = {
        "data_type": type(data).__name__,
        "keys": list(data.keys()) if isinstance(data, dict) else None,
        "length": len(data) if isinstance(data, (list, dict)) else None,
    }

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "json",
        "file_hash": fhash,
        "title": filename,
        "full_text": full_text,
        "pages": [{"page": 1, "text": full_text}],
        "metadata": metadata,
        "structured_data": data,
        "extraction_method": "json-parse",
    }