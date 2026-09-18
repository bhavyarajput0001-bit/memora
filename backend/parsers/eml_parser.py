"""EML (email) parser -- preserves sender, recipient, subject, timestamp, body."""
import email
from email import policy
from email.parser import BytesParser

from backend.utils import generate_id, file_hash, parse_date_flexible


def parse_eml(file_path: str, filename: str, raw_bytes: bytes) -> dict:
    """Parse an .eml email file."""
    doc_id = generate_id("doc_")
    fhash = file_hash(raw_bytes)

    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    except Exception:
        return {
            "id": doc_id,
            "filename": filename,
            "source_type": "eml",
            "file_hash": fhash,
            "title": filename,
            "full_text": raw_bytes.decode("utf-8", errors="replace"),
            "pages": [{"page": 1, "text": raw_bytes.decode("utf-8", errors="replace")}],
            "metadata": {"parse_error": True},
            "extraction_method": "email-parse-failed",
        }

    subject = msg.get("subject", "")
    sender = msg.get("from", "")
    recipient = msg.get("to", "")
    date_str = msg.get("date", "")
    timestamp = parse_date_flexible(date_str) if date_str else None

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    body = part.get_content()
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_content()
        except Exception:
            body = str(msg)

    metadata = {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "date": date_str,
        "timestamp": timestamp.isoformat() if timestamp else None,
        "message_id": msg.get("message-id", ""),
    }

    full_text = f"From: {sender}\nTo: {recipient}\nSubject: {subject}\nDate: {date_str}\n\n{body}"

    return {
        "id": doc_id,
        "filename": filename,
        "source_type": "eml",
        "file_hash": fhash,
        "title": subject or filename,
        "full_text": full_text,
        "pages": [{"page": 1, "text": full_text}],
        "metadata": metadata,
        "extraction_method": "email-parser",
    }
