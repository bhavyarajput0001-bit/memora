"""MEMORA document ingestion pipeline.

FILE → TYPE DETECTION → PARSING → NORMALIZATION → METADATA EXTRACTION →
CHUNKING → ENTITY EXTRACTION → EVENT EXTRACTION → FACT EXTRACTION → INDEXING → MEMORY UPDATE
"""
import os
import hashlib
from datetime import datetime
from typing import Optional

from backend.config import MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS, UPLOAD_DIR
from backend.db import get_session
from backend.models import Document, Chunk, Entity, Fact, Relationship, Event
from backend.parsers import get_parser
from backend.utils import generate_id, file_hash, utcnow, normalize_whitespace
from backend.services import chunker, extraction


def detect_source_type(filename: str) -> Optional[str]:
    ext = os.path.splitext(filename)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext.lstrip(".")
    return None


def validate_file(filename: str, size: int) -> tuple[bool, str]:
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large: {size} bytes (max {MAX_FILE_SIZE_MB}MB)"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}"
    return True, "ok"


def save_upload(file_bytes: bytes, filename: str) -> str:
    """Save uploaded file to disk. Returns the storage path."""
    safe_name = os.path.basename(filename)
    storage_path = UPLOAD_DIR / safe_name
    # Avoid overwriting — add suffix if exists
    counter = 1
    while storage_path.exists():
        base, ext = os.path.splitext(safe_name)
        storage_path = UPLOAD_DIR / f"{base}_{counter}{ext}"
        counter += 1
    with open(storage_path, "wb") as f:
        f.write(file_bytes)
    return str(storage_path)


def ingest(file_bytes: bytes, filename: str) -> dict:
    """Full ingestion pipeline. Returns the parsed document dict."""
    valid, msg = validate_file(filename, len(file_bytes))
    if not valid:
        raise ValueError(msg)

    source_type = detect_source_type(filename)
    if not source_type:
        raise ValueError(f"Cannot determine source type for: {filename}")

    parser = get_parser(source_type)
    if not parser:
        raise ValueError(f"No parser for source type: {source_type}")

    # Save file
    storage_path = save_upload(file_bytes, filename)

    # Parse
    parsed = parser(storage_path, filename, file_bytes)
    parsed["storage_path"] = storage_path
    parsed["upload_time"] = utcnow().isoformat()

    # Chunk the full text
    chunks = chunker.chunk_text(parsed["full_text"], parsed)
    parsed["chunks"] = chunks

    # Extract entities, events, facts
    extraction = extractor.extract_all(parsed)
    parsed["extraction"] = extraction

    return parsed


def persist_document(parsed: dict) -> str:
    """Persist a parsed document and its chunks to the database."""
    with get_session() as db:
        doc = Document(
            id=parsed["id"],
            filename=parsed["filename"],
            source_type=parsed["source_type"],
            file_hash=parsed["file_hash"],
            title=parsed.get("title"),
            extraction_method=parsed.get("extraction_method"),
            original_location=parsed.get("storage_path"),
            metadata_json=parsed.get("metadata", {}),
            page_count=len(parsed.get("pages", [])),
        )
        db.add(doc)
        db.flush()

        # Persist chunks
        for ch in parsed.get("chunks", []):
            chunk = Chunk(
                id=ch["id"],
                document_id=doc.id,
                page=ch.get("page"),
                section=ch.get("section"),
                position=ch.get("position", 0),
                text=ch["text"],
                metadata_json=ch.get("metadata", {}),
            )
            db.add(chunk)

        # Persist entities
        entity_map = {}
        for ent in parsed.get("extraction", {}).get("entities", []):
            entity = Entity(
                id=ent["id"],
                canonical_name=ent["canonical_name"],
                entity_type=ent["entity_type"],
                aliases_json=ent.get("aliases", []),
                sources_json=ent.get("sources", []),
                confidence=ent.get("confidence", 0.5),
            )
            db.add(entity)
            entity_map[ent["canonical_name"].lower()] = entity.id

        # Persist facts
        for fact in parsed.get("extraction", {}).get("facts", []):
            f = Fact(
                id=fact["id"],
                subject=fact["subject"],
                predicate=fact["predicate"],
                object=fact["object"],
                source_id=doc.id,
                source_location=fact.get("source_location", {}),
                observed_at=fact.get("observed_at"),
                effective_at=fact.get("effective_at"),
                confidence=fact.get("confidence", 0.8),
                status=fact.get("status", "likely_current"),
                relationship=fact.get("relationship"),
                conflict_state="none",
            )
            db.add(f)

        # Persist events
        for evt in parsed.get("extraction", {}).get("events", []):
            event = Event(
                id=evt["id"],
                title=evt["title"],
                start_at=evt["start_at"],
                end_at=evt.get("end_at"),
                location=evt.get("location"),
                participants_json=evt.get("participants", []),
                description=evt.get("description"),
                source_id=doc.id,
                source_location=evt.get("source_location", {}),
                observed_at=evt.get("observed_at"),
                confidence=evt.get("confidence", 0.8),
            )
            db.add(event)

        db.commit()
        return doc.id