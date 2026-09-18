"""Plain text / Markdown parser."""
from backend.utils import generate_id, file_hash


def parse_text(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse a TXT or MD file."""
    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1", errors="replace")

    lines = text.split("\n")
    pages = [{"page": 1, "text": text}]
    metadata = {"line_count": len(lines), "char_count": len(text)}

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "md" if filename.endswith(".md") else "txt",
        "file_hash": fhash,
        "title": filename,
        "full_text": text,
        "pages": pages,
        "metadata": metadata,
        "extraction_method": "utf-8-decode",
    }