"""MEMORA ingestion API route."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional

from backend.services import ingestion

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


@router.post("/file")
async def ingest_file(
    file: UploadFile = File(...),
    title: Optional[str] = None,
):
    """Upload and ingest a document."""
    file_bytes = await file.read()
    filename = file.filename or "unknown"
    
    try:
        parsed = ingestion.ingest(file_bytes, filename)
        if title:
            parsed["title"] = title
        doc_id = ingestion.persist_document(parsed)
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": parsed["filename"],
            "source_type": parsed["source_type"],
            "title": parsed.get("title"),
            "chunks_created": len(parsed.get("chunks", [])),
            "entities_found": len(parsed.get("extraction", {}).get("entities", [])),
            "facts_extracted": len(parsed.get("extraction", {}).get("facts", [])),
            "events_extracted": len(parsed.get("extraction", {}).get("events", [])),
            "message": "Document ingested successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/text")
async def ingest_text(
    text: str,
    title: Optional[str] = None,
    source_type: str = "txt",
    filename: Optional[str] = None,
):
    """Ingest raw text."""
    filename = filename or "text_input.txt"
    file_bytes = text.encode("utf-8")
    
    try:
        parsed = ingestion.ingest(file_bytes, filename)
        if title:
            parsed["title"] = title
        doc_id = ingestion.persist_document(parsed)
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": filename,
            "source_type": source_type,
            "title": title or filename,
            "chunks_created": len(parsed.get("chunks", [])),
            "entities_found": len(parsed.get("extraction", {}).get("entities", [])),
            "facts_extracted": len(parsed.get("extraction", {}).get("facts", [])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/status")
async def get_ingest_status():
    """Get ingestion statistics."""
    from backend.db import get_session
    from backend.models import Document
    with get_session() as db:
        doc_count = db.query(Document).count()
        return {
            "total_documents": doc_count,
            "message": f"Database contains {doc_count} documents",
        }
