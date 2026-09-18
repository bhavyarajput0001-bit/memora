"""MEMORA document search/retrieval API route."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from backend.db import get_session
from backend.models import Document, Chunk, Fact, Entity
from backend.services import retrieval

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


class SearchRequest(BaseModel):
    query: str
    source_type: Optional[str] = None
    limit: int = 10


class DocumentDetail(BaseModel):
    id: str
    filename: str
    source_type: str
    title: Optional[str]
    page_count: Optional[int]
    upload_time: str
    fact_count: int
    entity_count: int
    snippet: str


@router.get("/")
async def list_documents(
    source_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    """List all documents with optional type filter."""
    with get_session() as db:
        query = db.query(Document)
        if source_type:
            query = query.filter(Document.source_type == source_type)
        
        docs = (
            query
            .order_by(Document.upload_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # Get counts for each document
        results = []
        for doc in docs:
            fact_count = db.query(Fact).filter(Fact.source_id == doc.id).count()
            entity_count = db.query(Entity).filter(Entity.sources_json.contains([doc.id])).count()
            
            results.append({
                "id": doc.id,
                "filename": doc.filename,
                "source_type": doc.source_type,
                "title": doc.title,
                "page_count": doc.page_count,
                "upload_time": doc.upload_time.isoformat(),
                "fact_count": fact_count,
                "entity_count": entity_count,
            })
        
        return {
            "documents": results,
            "total": len(results),
        }


@router.post("/search")
async def search_documents(request: SearchRequest):
    """Search documents by query using hybrid search."""
    try:
        results = retrieval.hybrid_search(
            query=request.query,
            limit=request.limit,
            source_type=request.source_type,
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{doc_id}")
async def get_document_detail(doc_id: str):
    """Get detailed information about a document including its chunks and facts."""
    with get_session() as db:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks
        chunks = (
            db.query(Chunk)
            .filter(Chunk.document_id == doc_id)
            .order_by(Chunk.position)
            .all()
        )
        
        # Get facts
        facts = (
            db.query(Fact)
            .filter(Fact.source_id == doc_id)
            .all()
        )
        
        # Get entities
        entities = []
        for fact in facts[:20]:  # Limit to avoid heavy queries
            # Parse subject/object to find entities
            pass
        
        return {
            "document": {
                "id": doc.id,
                "filename": doc.filename,
                "source_type": doc.source_type,
                "title": doc.title,
                "page_count": doc.page_count,
                "upload_time": doc.upload_time.isoformat(),
                "extraction_method": doc.extraction_method,
            },
            "chunks": [
                {
                    "id": c.id,
                    "page": c.page,
                    "section": c.section,
                    "text": c.text[:500],
                    "position": c.position,
                }
                for c in chunks[:50]  # Limit chunks
            ],
            "facts": [
                {
                    "subject": f.subject,
                    "predicate": f.predicate,
                    "object": f.object,
                    "confidence": f.confidence,
                    "status": f.status,
                }
                for f in facts[:20]
            ],
            "stats": {
                "total_chunks": len(chunks),
                "total_facts": len(facts),
            }
        }


@router.get("/{doc_id}/chunks")
async def get_document_chunks(
    doc_id: str,
    page: Optional[int] = None,
    limit: int = 20,
):
    """Get chunks for a specific document with optional pagination."""
    with get_session() as db:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        query = db.query(Chunk).filter(Chunk.document_id == doc_id)
        if page is not None:
            query = query.filter(Chunk.page == page)
        
        chunks = query.order_by(Chunk.position).limit(limit).all()
        
        return {
            "document_id": doc_id,
            "chunks": [
                {
                    "id": c.id,
                    "page": c.page,
                    "section": c.section,
                    "text": c.text,
                    "position": c.position,
                }
                for c in chunks
            ],
            "total": len(chunks),
        }
