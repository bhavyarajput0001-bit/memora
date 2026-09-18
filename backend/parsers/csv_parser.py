"""CSV parser — preserves structured fields."""
import csv
import io

from backend.utils import generate_id, file_hash


def parse_csv(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse a CSV file. Returns structured rows + text representation."""
    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1", errors="replace")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return {
            "id": doc_id,
            "filename": filename,
            "source_type": "csv",
            "file_hash": fhash,
            "title": filename,
            "full_text": "",
            "pages": [{"page": 1, "text": ""}],
            "metadata": {"row_count": 0},
            "extraction_method": "csv-reader",
        }

    headers = rows[0]
    data_rows = rows[1:]

    # Build a text representation for retrieval
    text_lines = [", ".join(headers)]
    for row in data_rows:
        text_lines.append(", ".join(row))
    full_text = "\n".join(text_lines)

    metadata = {
        "headers": headers,
        "row_count": len(data_rows),
        "column_count": len(headers),
    }

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "csv",
        "file_hash": fhash,
        "title": filename,
        "full_text": full_text,
        "pages": [{"page": 1, "text": full_text}],
        "metadata": metadata,
        "structured_rows": [{"headers": headers, "row": r} for r in data_rows],
        "extraction_method": "csv-reader",
    }