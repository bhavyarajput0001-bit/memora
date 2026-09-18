"""MEMORA sources API route."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.db import get_session
from backend.models import Document, Chunk

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


@router.get("/")
async def get_sources(limit: int = 20):
    """List all sources."""
    with get_session() as db:
        docs = (
            db.query(Document)
            .order_by(Document.upload_time.desc())
            .limit(limit)
            .all()
        )
        return {
            "sources": [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "source_type": d.source_type,
                    "title": d.title,
                    "page_count": d.page_count,
                    "upload_time": d.upload_time.isoformat(),
                }
                for d in docs
            ],
            "count": len(docs),
        }


@router.get("/{doc_id}")
async def get_source_details(doc_id: str):
    """Get detailed information about a source."""
    with get_session() as db:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Source not found")
        
        chunks = db.query(Chunk).filter(Chunk.document_id == doc_id).all()
        
        return {
            "id": doc.id,
            "filename": doc.filename,
            "source_type": doc.source_type,
            "title": doc.title,
            "page_count": doc.page_count,
            "upload_time": doc.upload_time.isoformat(),
            "extraction_method": doc.extraction_method,
            "file_hash": doc.file_hash,
            "chunks": [
                {
                    "id": c.id,
                    "page": c.page,
                    "section": c.section,
                    "position": c.position,
                    "text": c.text,
                }
                for c in chunks
            ],
            "chunk_count": len(chunks),
        }


@router.get("/{doc_id}/chunks")
async def get_source_chunks(doc_id: str, page: Optional[int] = None):
    """Get chunks for a source."""
    with get_session() as db:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Source not found")
        
        q = db.query(Chunk).filter(Chunk.document_id == doc_id)
        if page is not None:
            q = q.filter(Chunk.page == page)
        chunks = q.all()
        return {
            "source_id": doc_id,
            "source_type": doc.source_type,
            "chunks": [
                {
                    "id": c.id,
                    "page": c.page,
                    "section": c.section,
                    "position": c.position,
                    "text": c.text,
                }
                for c in chunks
            ],
            "count": len(chunks),
        }
