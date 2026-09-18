"""MEMORA utility functions — hashing, text, temporal, tracing."""
import hashlib
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional


def generate_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def truncate_text(text: str, max_chars: int = 500) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars // 2] + " ... " + text[-max_chars // 2:]


def parse_date_flexible(s: str) -> Optional[datetime]:
    """Parse a date string in various formats. Returns datetime or None."""
    if not s:
        return None
    s = s.strip()
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # Try ISO format
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    return None


def relative_date(reference: datetime, days: int) -> datetime:
    return reference + timedelta(days=days)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def safe_json_default(obj):
    """JSON default handler for non-serializable objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    return str(obj)