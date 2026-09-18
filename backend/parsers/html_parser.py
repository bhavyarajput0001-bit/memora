"""HTML parser."""
from backend.utils import generate_id, file_hash
import re


def parse_html(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse an HTML file -- strips tags for text."""
    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1", errors="replace")

    # Try to extract title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else filename

    # Strip tags for text content
    clean = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    clean = re.sub(r"<style[^>]*>.*?</style>", " ", clean, flags=re.IGNORECASE | re.DOTALL)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "html",
        "file_hash": fhash,
        "title": title,
        "full_text": clean,
        "pages": [{"page": 1, "text": clean}],
        "metadata": {"title": title},
        "extraction_method": "html-strip-tags",
    }
