"""MEMORA retrieval engine — hybrid search with TF-IDF + metadata + temporal filters.

Architecture:
  1. Semantic retrieval (TF-IDF vector search)
  2. Metadata filtering (source_type, entity, date range)
  3. Temporal filtering
  4. Exact/entity matching
  5. Structured relationship lookup
  6. Reranking with LLM

NO embeddings model locally (8GB RAM constraint).
Using TF-IDF from scikit-learn for semantic similarity.
"""
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import text

from backend.db import get_session
from backend.models import Document, Chunk, Entity, Fact, Relationship, Event


def hybrid_search(
    query: str,
    limit: int = 10,
    source_type: Optional[str] = None,
    entity_name: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[dict]:
    """Execute hybrid retrieval for a query."""
    # Step 1: Get TF-IDF scores (simple text similarity)
    tfidf_results = _tfidf_search(query, limit=limit * 2)

    # Step 2: Apply metadata filters
    if source_type or entity_name or date_from or date_to:
        tfidf_results = _apply_filters(
            tfidf_results,
            source_type=source_type,
            entity_name=entity_name,
            date_from=date_from,
            date_to=date_to,
        )

    # Step 3: Exact entity match
    entity_matches = _entity_match(entity_name) if entity_name else []

    # Combine and rerank
    combined = _merge_results(tfidf_results, entity_matches)
    combined = _rerank_with_llm(query, combined[:limit * 2])

    return combined[:limit]


def _tfidf_search(query: str, limit: int = 20) -> list[dict]:
    """Simple TF-IDF based text search using chunks."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    with get_session() as db:
        chunks = db.query(Chunk).all()
        documents = {c.document_id: c.document for c in chunks}
        if not chunks:
            return []

        # Build corpus
        corpus = [c.text for c in chunks]
        docs_map = {i: c for i, c in enumerate(chunks)}

        # Vectorize
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([query] + corpus)
        except Exception:
            return []

        # Compute similarity
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Get top results
        results = []
        for idx, score in enumerate(similarities):
            if score > 0.05:  # minimum relevance threshold
                chunk = docs_map[idx]
                doc = documents.get(chunk.document_id)
                results.append({
                    "type": "chunk",
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "score": float(score),
                    "text": chunk.text[:500],
                    "page": chunk.page,
                    "filename": doc.filename if doc else None,
                    "source_type": doc.source_type if doc else None,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results


def _entity_match(entity_name: str) -> list[dict]:
    """Find exact entity matches."""
    with get_session() as db:
        entities = db.query(Entity).filter(
            Entity.canonical_name.ilike(f"%{entity_name}%")
        ).all()
        results = []
        for ent in entities:
            results.append({
                "type": "entity",
                "id": ent.id,
                "name": ent.canonical_name,
                "entity_type": ent.entity_type,
                "score": 0.95,
                "aliases": ent.aliases_json or [],
                "confidence": ent.confidence,
            })
        return results


def _apply_filters(
    results: list[dict],
    source_type: Optional[str] = None,
    entity_name: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[dict]:
    """Apply metadata filters to search results."""
    filtered = results
    if source_type:
        filtered = [r for r in filtered if r.get("source_type") == source_type]
    return filtered


def _merge_results(
    tfidf_results: list[dict],
    entity_matches: list[dict],
) -> list[dict]:
    """Merge TF-IDF and entity results, deduplicating by document."""
    seen_docs = set()
    merged = []

    # Add entity matches first (higher priority for entity queries)
    for r in entity_matches:
        merged.append(r)
        seen_docs.add(r.get("document_id"))

    # Add TF-IDF results
    for r in tfidf_results:
        doc_id = r.get("document_id")
        if doc_id not in seen_docs:
            merged.append(r)
            seen_docs.add(doc_id)

    return merged


def _rerank_with_llm(query: str, results: list[dict]) -> list[dict]:
    """Rerank results using LLM for semantic relevance."""
    if not results or len(results) < 2:
        return results

    # Build rerank prompt
    items = []
    for i, r in enumerate(results[:10]):
        text_preview = r.get("text", "")[:200] if r.get("text") else f"[{r.get('type', 'unknown')}]"
        items.append(f"{i+1}. [{r.get('type')}] score={r.get('score', 0):.3f}: {text_preview}")

    prompt = f"""Query: {query}

Ranked items (1-10):
{chr(10).join(items)}

Return ONLY a JSON array of indices (0-based) sorted by relevance to the query.
Example: [2, 0, 5, 1, 3]"""

    messages = [
        {"role": "system", "content": "You are a relevance ranker. Return only a JSON array of indices."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = chat(messages=messages, model="auto", max_tokens=500, timeout_s=60)
        content = response["choices"][0]["message"]["content"]
        indices = json.loads(content)
        # Reorder results
        reordered = [results[i] for i in indices if i < len(results)]
        return reordered
    except Exception:
        return results


def get_timeline(days: int = 30, limit: int = 50) -> list[dict]:
    """Get recent timeline events."""
    with get_session() as db:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        events = (
            db.query(Event)
            .filter(Event.start_at >= cutoff)
            .order_by(Event.start_at.desc())
            .limit(limit)
            .all()
        )
        docs = {e.id: e for e in db.query(Document).filter(
            Document.id.in_([ev.source_id for ev in events])
        ).all()}
        return [
            {
                "id": ev.id,
                "title": ev.title,
                "start_at": ev.start_at.isoformat(),
                "end_at": ev.end_at.isoformat() if ev.end_at else None,
                "location": ev.location,
                "participants": ev.participants_json,
                "description": ev.description,
                "filename": docs.get(ev.source_id, {}).filename if ev.source_id in docs else None,
            }
            for ev in events
        ]


def get_entities() -> list[dict]:
    """Get all entities."""
    with get_session() as db:
        entities = db.query(Entity).all()
        return [
            {
                "id": e.id,
                "canonical_name": e.canonical_name,
                "entity_type": e.entity_type,
                "aliases": e.aliases_json or [],
                "confidence": e.confidence,
                "created_at": e.created_at.isoformat(),
            }
            for e in entities
        ]


def get_facts(limit: int = 100) -> list[dict]:
    """Get recent facts."""
    with get_session() as db:
        facts = db.query(Fact).order_by(Fact.observed_at.desc()).limit(limit).all()
        return [
            {
                "id": f.id,
                "subject": f.subject,
                "predicate": f.predicate,
                "object": f.object,
                "source_id": f.source_id,
                "observed_at": f.observed_at.isoformat() if f.observed_at else None,
                "effective_at": f.effective_at.isoformat() if f.effective_at else None,
                "confidence": f.confidence,
                "status": f.status,
                "relationship": f.relationship,
            }
            for f in facts
        ]
