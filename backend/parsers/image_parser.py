"""Image parser -- extracts OCR text via Pillow + preserves image reference."""
from backend.utils import generate_id, file_hash


def parse_image(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse a PNG/JPG image. Extracts OCR text if available, preserves image reference."""
    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    from PIL import Image
    import io

    try:
        img = Image.open(io.BytesIO(raw_bytes))
        width, height = img.size
        mode = img.mode
    except Exception:
        width = height = 0
        mode = "unknown"

    # Try OCR if pytesseract is available
    ocr_text = ""
    try:
        import pytesseract
        img = Image.open(io.BytesIO(raw_bytes))
        ocr_text = pytesseract.image_to_string(img).strip()
    except Exception:
        pass

    metadata = {
        "width": width,
        "height": height,
        "mode": mode,
        "has_ocr": bool(ocr_text),
    }

    full_text = ocr_text or f"[Image: {filename}, {width}x{height}]"

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "png" if filename.lower().endswith(".png") else "jpg",
        "file_hash": fhash,
        "title": filename,
        "full_text": full_text,
        "pages": [{"page": 1, "text": full_text}],
        "metadata": metadata,
        "extraction_method": "pillow" + ("+pytesseract" if ocr_text else ""),
    }
