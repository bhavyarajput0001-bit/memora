"""MEMORA document parsers — PDF, TXT, MD, CSV, JSON, EML, PNG/JPG, HTML, DOCX."""
from typing import Optional

from backend.parsers.pdf_parser import parse_pdf
from backend.parsers.text_parser import parse_text
from backend.parsers.csv_parser import parse_csv
from backend.parsers.json_parser import parse_json_file
from backend.parsers.eml_parser import parse_eml
from backend.parsers.image_parser import parse_image
from backend.parsers.html_parser import parse_html

PARSERS = {
    "pdf": parse_pdf,
    "txt": parse_text,
    "md": parse_text,
    "csv": parse_csv,
    "json": parse_json_file,
    "eml": parse_eml,
    "png": parse_image,
    "jpg": parse_image,
    "jpeg": parse_image,
    "html": parse_html,
}


def get_parser(source_type: str):
    return PARSERS.get(source_type)