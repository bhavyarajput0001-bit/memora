"""Relationship inference service for MEMORA."""
import logging
from typing import Optional
from collections import defaultdict

from backend.db import get_session
from backend.models import Entity, Fact, Relationship, Chunk
from backend.services.embeddings import encode_single, cosine_similarity

logger = logging.getLogger(__name__)


def infer_relationships() -> list[dict]:
    """
    Infer new relationships from existing facts and co-occurrence patterns.
    Returns list of inferred relationships.
    """
    with get_session() as db:
        facts = db.query(Fact).all()
        entities = db.query(Entity).all()

        # Build entity-fact map
        entity_facts = defaultdict(list)
        for fact in facts:
            entity_facts[fact.subject].append(fact)
            if fact.object:
                entity_facts[fact.object].append(fact)

        # Find entities that frequently appear together
        entity_cooccurrence = defaultdict(lambda: defaultdict(int))
        for fact in facts:
            if fact.subject and fact.object:
                entity_cooccurrence[fact.subject][fact.object] += 1
                entity_cooccurrence[fact.object][fact.subject] += 1

        # Infer relationships
        inferred = []
        for ent1, neighbors in entity_cooccurrence.items():
            for ent2, count in neighbors.items():
                if ent1 >= ent2:
                    continue
                if count >= 2:  # At least 2 co-occurrences
                    inferred.append({
                        "subject": ent1,
                        "object": ent2,
                        "predicate": "related_to",
                        "confidence": min(count * 0.3, 0.9),
                        "source": "co_occurrence",
                        "strength": count,
                    })

        return inferred


def get_entity_relationships(entity_name: str) -> list[dict]:
    """Get all relationships for an entity."""
    with get_session() as db:
        facts = db.query(Fact).filter(
            (Fact.subject == entity_name) | (Fact.object == entity_name)
        ).all()

        relationships = []
        for fact in facts:
            other = fact.object if fact.subject == entity_name else fact.subject
            relationships.append({
                "subject": fact.subject,
                "predicate": fact.predicate,
                "object": fact.object,
                "confidence": fact.confidence,
                "source_id": fact.source_id,
            })

        return relationships


def search_relationships(query: str, limit: int = 10) -> list[dict]:
    """Search for relationships matching a query."""
    with get_session() as db:
        facts = db.query(Fact).all()

        query_lower = query.lower()
        results = []

        for fact in facts:
            # Check if query matches subject, predicate, or object
            score = 0.0
            if query_lower in fact.subject.lower():
                score += 0.5
            if query_lower in fact.predicate.lower():
                score += 0.5
            if fact.object and query_lower in fact.object.lower():
                score += 0.3

            if score > 0:
                results.append({
                    "subject": fact.subject,
                    "predicate": fact.predicate,
                    "object": fact.object,
                    "score": score,
                    "confidence": fact.confidence,
                    "source_id": fact.source_id,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
