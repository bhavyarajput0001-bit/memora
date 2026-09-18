"""PDF parser using pypdf — preserves page boundaries."""
from typing import Optional

from backend.utils import generate_id, file_hash, truncate_text


def parse_pdf(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse a PDF file. Returns structured content with page boundaries."""
    from pypdf import PdfReader
    import io

    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    reader = PdfReader(io.BytesIO(raw_bytes))
    pages = []
    full_text_parts = []
    page_count = len(reader.pages)

    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = text.strip()
        pages.append({
            "page": i + 1,
            "text": text,
        })
        full_text_parts.append(text)

    full_text = "\n\n".join(full_text_parts)

    # Metadata
    metadata = {}
    try:
        info = reader.metadata
        if info:
            metadata["author"] = info.author
            metadata["title"] = info.title
            metadata["subject"] = info.subject
    except Exception:
        pass
    metadata["page_count"] = page_count

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "pdf",
        "file_hash": fhash,
        "title": metadata.get("title") or filename,
        "full_text": full_text,
        "pages": pages,
        "metadata": metadata,
        "extraction_method": "pypdf",
    }