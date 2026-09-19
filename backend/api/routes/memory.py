"""MEMORA memory API route."""
from fastapi import APIRouter
from typing import Optional

from backend.services import retrieval
from backend.db import get_session
from backend.models import Document, Entity, Fact

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.get("/")
async def get_memory(limit: int = 50, offset: int = 0):
    """Get memory summary and recent facts."""
    with get_session() as db:
        doc_count = db.query(Document).count()
        entity_count = db.query(Entity).count()
        fact_count = db.query(Fact).count()
        
        recent_facts = (
            db.query(Fact)
            .order_by(Fact.observed_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return {
            "total_documents": doc_count,
            "total_entities": entity_count,
            "total_facts": fact_count,
            "recent_facts": [
                {
                    "id": f.id,
                    "subject": f.subject,
                    "predicate": f.predicate,
                    "object": f.object,
                    "source_id": f.source_id,
                    "observed_at": f.observed_at.isoformat() if f.observed_at else None,
                    "confidence": f.confidence,
                    "status": f.status,
                }
                for f in recent_facts
            ],
        }


@router.get("/documents")
async def get_documents(limit: int = 20, offset: int = 0):
    """List all documents."""
    with get_session() as db:
        docs = (
            db.query(Document)
            .order_by(Document.upload_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "documents": [
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


@router.get("/entities")
async def get_entities(limit: int = 50):
    """Get all entities."""
    with get_session() as db:
        entities = (
            db.query(Entity)
            .order_by(Entity.confidence.desc())
            .limit(limit)
            .all()
        )
        return {
            "entities": [
                {
                    "id": e.id,
                    "name": e.canonical_name,
                    "entity_type": e.entity_type,
                    "aliases": e.aliases_json,
                    "sources": e.sources_json,
                    "confidence": e.confidence,
                }
                for e in entities
            ],
            "count": len(entities),
        }


@router.get("/facts")
async def get_facts(limit: int = 50):
    """Get facts."""
    with get_session() as db:
        facts = (
            db.query(Fact)
            .order_by(Fact.observed_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "facts": [
                {
                    "id": f.id,
                    "subject": f.subject,
                    "predicate": f.predicate,
                    "object": f.object,
                    "confidence": f.confidence,
                    "status": f.status,
                    "observed_at": f.observed_at.isoformat() if f.observed_at else None,
                    "effective_at": f.effective_at.isoformat() if f.effective_at else None,
                }
                for f in facts
            ],
            "count": len(facts),
        }
