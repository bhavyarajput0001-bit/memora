"""MEMORA chunking — semantic/document-aware chunks.

Uses headings, paragraphs, and page boundaries.
Avoids naive fixed-size chunks.
"""
import re
from typing import Optional

from backend.utils import generate_id


def chunk_text(full_text: str, parsed_doc: dict, max_chunk_chars: int = 2000) -> list[dict]:
    """Split text into semantic chunks preserving structure."""
    pages = parsed_doc.get("pages", [])
    chunks = []
    position = 0

    if not pages:
        # Single-page fallback
        return _chunk_single_page(full_text, 1, max_chunk_chars, position)

    for page in pages:
        page_num = page.get("page", 1)
        page_text = page.get("text", "")
        page_chunks = _chunk_single_page(page_text, page_num, max_chunk_chars, position)
        chunks.extend(page_chunks)
        position += len(page_chunks)

    return chunks


def _chunk_single_page(text: str, page: int, max_chars: int, start_pos: int) -> list[dict]:
    """Chunk a single page's text by headings and paragraphs."""
    if not text.strip():
        return []

    # Split by markdown headings or numbered sections
    heading_pattern = re.compile(
        r"(?:^|\n)(#{1,6}\s+[^\n]+|\d+\.\s+[^\n]+|[A-Z][A-Z\s]{3,}\n?=+\n?)",
        re.MULTILINE,
    )

    # Find heading positions
    parts = []
    last_end = 0
    for m in heading_pattern.finditer(text):
        if m.start() > last_end:
            parts.append(("body", text[last_end:m.start()]))
        parts.append(("heading", m.group(0)))
        last_end = m.end()
    if last_end < len(text):
        parts.append(("body", text[last_end:]))

    if not parts:
        parts = [("body", text)]

    # Build chunks — group body parts under headings
    chunks = []
    current_heading = None
    current_text = ""
    current_pos = start_pos

    for kind, content in parts:
        content = content.strip()
        if not content:
            continue
        if kind == "heading":
            # Flush current chunk
            if current_text.strip():
                chunks.append(_make_chunk(current_text, page, current_pos, current_heading))
                current_pos += 1
                current_text = ""
            current_heading = content
        else:
            # Add to current chunk, respecting max_chars
            if current_text:
                candidate = current_text + "\n\n" + content
            else:
                candidate = content

            if len(candidate) > max_chars and current_text:
                # Flush and start new
                chunks.append(_make_chunk(current_text, page, current_pos, current_heading))
                current_pos += 1
                current_text = content
            else:
                current_text = candidate

    if current_text.strip():
        chunks.append(_make_chunk(current_text, page, current_pos, current_heading))

    if not chunks:
        # Fallback: split by paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        current_text = ""
        for para in paragraphs:
            candidate = current_text + "\n\n" + para if current_text else para
            if len(candidate) > max_chars and current_text:
                chunks.append(_make_chunk(current_text, page, current_pos, current_heading))
                current_pos += 1
                current_text = para
            else:
                current_text = candidate
        if current_text.strip():
            chunks.append(_make_chunk(current_text, page, current_pos, current_heading))

    return chunks


def _make_chunk(text: str, page: int, position: int, section: Optional[str]) -> dict:
    return {
        "id": generate_id("chk_"),
        "page": page,
        "section": section,
        "position": position,
        "text": text.strip(),
        "metadata": {},
    }