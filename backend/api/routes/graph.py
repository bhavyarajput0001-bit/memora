"""Graph query API route for MEMORA."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services import entity_resolution, relationship_inference

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


class GraphQueryRequest(BaseModel):
    query: str
    limit: int = 10


class EntityResolveRequest(BaseModel):
    merge_duplicates: bool = True


@router.get("/entities/{entity_id}")
async def get_entity_details(entity_id: str):
    """Get detailed information about an entity."""
    from backend.db import get_session
    from backend.models import Entity, Fact
    with get_session() as db:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        facts = db.query(Fact).filter(
            (Fact.subject == entity.canonical_name) |
            (Fact.object == entity.canonical_name)
        ).all()

        return {
            "id": entity.id,
            "name": entity.canonical_name,
            "type": entity.entity_type,
            "aliases": entity.aliases_json,
            "sources": entity.sources_json,
            "confidence": entity.confidence,
            "facts": [
                {
                    "subject": f.subject,
                    "predicate": f.predicate,
                    "object": f.object,
                    "confidence": f.confidence,
                }
                for f in facts
            ],
        }


@router.post("/resolve")
async def resolve_entities(request: EntityResolveRequest):
    """Run entity resolution and merge duplicates."""
    if request.merge_duplicates:
        result = entity_resolution.resolve_entities()
        return {"success": True, "result": result}
    return {"success": True, "result": {"message": "No merges requested"}}


@router.get("/graph")
async def get_entity_graph():
    """Get the full entity relationship graph."""
    graph = entity_resolution.get_entity_graph()
    relationships = relationship_inference.infer_relationships()
    return {
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "inferred_relationships": relationships,
        "count": graph["count"],
    }


@router.post("/search")
async def search_entities(request: GraphQueryRequest):
    """Search entities by name with fuzzy matching."""
    results = entity_resolution.search_entities(request.query, limit=request.limit)
    return {"results": results, "count": len(results)}


@router.get("/relationships/{entity_name}")
async def get_entity_relationships(entity_name: str):
    """Get all relationships for an entity."""
    relationships = relationship_inference.get_entity_relationships(entity_name)
    return {"relationships": relationships, "count": len(relationships)}


@router.post("/relationships/search")
async def search_relationships(request: GraphQueryRequest):
    """Search relationships by query."""
    results = relationship_inference.search_relationships(request.query, limit=request.limit)
    return {"results": results, "count": len(results)}
