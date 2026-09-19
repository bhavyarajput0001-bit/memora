"""Entity resolution service for MEMORA — merge duplicate entities."""
import logging
from datetime import datetime
from typing import Optional
from collections import defaultdict

from backend.db import get_session
from backend.models import Entity, Chunk
from backend.services.embeddings import encode_single, cosine_similarity

logger = logging.getLogger(__name__)

# Minimum similarity to consider two entities as potential duplicates
ENTITY_SIMILARITY_THRESHOLD = 0.75
# Minimum name similarity for string-based matching
NAME_SIMILARITY_THRESHOLD = 0.8


def resolve_entities() -> dict:
    """
    Run entity resolution: find and merge duplicate entities.
    Returns stats about what was merged.
    """
    with get_session() as db:
        entities = db.query(Entity).all()
        if len(entities) <= 1:
            return {"merged": 0, "duplicates_found": 0, "entities_count": len(entities)}

        # Build similarity graph
        merges = []
        merged_ids = set()

        for i, ent_i in enumerate(entities):
            if ent_i.id in merged_ids:
                continue

            for j, ent_j in enumerate(entities[i+1:], i+1):
                if ent_j.id in merged_ids:
                    continue

                # Check if entities should be merged
                should_merge, reason = _should_merge(ent_i, ent_j)
                if should_merge:
                    merges.append({
                        "keep": ent_i.id,
                        "merge_into": ent_j.id,
                        "reason": reason,
                    })
                    merged_ids.add(ent_j.id)
                    # Update aliases
                    ent_i.aliases_json = list(set(
                        ent_i.aliases_json + [ent_j.canonical_name] + ent_j.aliases_json
                    ))
                    ent_i.sources_json = list(set(ent_i.sources_json + ent_j.sources_json))

        # Commit merges
        db.commit()

        return {
            "merged": len(merges),
            "duplicates_found": len(merges),
            "entities_count": len(entities) - len(merged_ids),
            "merge_details": merges,
        }


def _should_merge(ent_i: Entity, ent_j: Entity) -> tuple[bool, str]:
    """Check if two entities should be merged."""
    # Exact name match
    if ent_i.canonical_name.lower() == ent_j.canonical_name.lower():
        return True, "exact_name_match"

    # Alias match
    if ent_j.canonical_name.lower() in [a.lower() for a in ent_i.aliases_json]:
        return True, "alias_match"

    # Similarity-based match
    name1 = ent_i.canonical_name.lower()
    name2 = ent_j.canonical_name.lower()

    # Simple string similarity
    if _text_similarity(name1, name2) >= NAME_SIMILARITY_THRESHOLD:
        return True, "name_similarity"

    return False, ""


def _text_similarity(s1: str, s2: str) -> float:
    """Calculate text similarity using character overlap."""
    if not s1 or not s2:
        return 0.0
    # Use set-based Jaccard similarity
    set1 = set(s1.split())
    set2 = set(s2.split())
    if not set1 or not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) if union else 0.0


def get_entity_graph() -> dict:
    """
    Get entity relationship graph.
    Returns nodes and edges for visualization.
    """
    with get_session() as db:
        entities = db.query(Entity).all()
        chunks = db.query(Chunk).all()

        # Build entity-chunk relationships
        entity_chunks = defaultdict(list)
        for chunk in chunks:
            meta = chunk.metadata_json or {}
            entities_in_chunk = meta.get("entities", [])
            for ent_name in entities_in_chunk:
                entity_chunks[ent_name].append(chunk.id)

        nodes = []
        edges = []

        for ent in entities:
            nodes.append({
                "id": ent.id,
                "label": ent.canonical_name,
                "type": ent.entity_type,
                "confidence": ent.confidence,
                "alias_count": len(ent.aliases_json),
                "source_count": len(ent.sources_json),
            })

            # Create edges to chunks
            for chunk_id in entity_chunks.get(ent.canonical_name, []):
                edges.append({
                    "from": ent.id,
                    "to": f"chunk_{chunk_id}",
                    "type": "mentioned_in",
                })

        # Find co-occurrence edges (entities appearing in same chunks)
        entity_chunk_map = defaultdict(set)
        for chunk in chunks:
            meta = chunk.metadata_json or {}
            for ent_name in meta.get("entities", []):
                entity_chunk_map[ent_name].add(chunk.id)

        seen_edges = set()
        for ent1, chunks1 in entity_chunk_map.items():
            for ent2, chunks2 in entity_chunk_map.items():
                if ent1 >= ent2:
                    continue
                overlap = chunks1 & chunks2
                if overlap:
                    edge_key = (ent1, ent2)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        nodes.append({"id": ent1, "label": ent1, "type": "PERSON"})
                        nodes.append({"id": ent2, "label": ent2, "type": "PERSON"})
                        edges.append({
                            "from": ent1,
                            "to": ent2,
                            "type": "co_occurrence",
                            "strength": len(overlap),
                        })

        return {"nodes": nodes, "edges": edges, "count": len(nodes)}


def search_entities(query: str, limit: int = 10) -> list[dict]:
    """Search entities by name with fuzzy matching."""
    with get_session() as db:
        entities = db.query(Entity).all()

        query_lower = query.lower()
        results = []

        for ent in entities:
            score = 0.0
            name_lower = ent.canonical_name.lower()

            # Exact match gets highest score
            if name_lower == query_lower:
                score = 1.0
            # Contains match
            elif query_lower in name_lower:
                score = 0.8
            # Partial word match
            elif any(word in name_lower for word in query_lower.split()):
                score = 0.6
            # Alias match
            elif any(query_lower in alias.lower() for alias in ent.aliases_json):
                score = 0.7

            if score > 0:
                results.append({
                    "id": ent.id,
                    "name": ent.canonical_name,
                    "entity_type": ent.entity_type,
                    "score": score,
                    "aliases": ent.aliases_json,
                    "sources": ent.sources_json,
                    "confidence": ent.confidence,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
