"""
Embedding-backed retrieval for MEMORA.

Replaces pure TF-IDF with:
  1. Embedding similarity (semantic)
  2. TF-IDF (keyword)
  3. Exact entity match
  4. LLM rerank over the union

Usage:
    results = hybrid_search("when is the deadline?")
"""
import json
import logging
from datetime import datetime
from typing import Optional

import numpy as np
from sqlalchemy import text

from backend.config.embeddings import EMBEDDING_DIM, EMBEDDING_MAX_LENGTH
from backend.db import get_session
from backend.llm import chat
from backend.models import Document, Chunk, Entity
from backend.services.embeddings import encode_batch, cosine_similarity

logger = logging.getLogger(__name__)

# Minimum cosine similarity threshold for embedding matches
EMB_MIN_SCORE = 0.25
# TF-IDF minimum threshold
TFIDF_MIN_SCORE = 0.05
# How many candidates to pass to the LLM reranker
RERANK_CANDIDATES = 15
# Final result limit
FINAL_LIMIT = 10


def hybrid_search(
    query: str,
    limit: int = 10,
    source_type: Optional[str] = None,
    entity_name: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[dict]:
    """Execute hybrid retrieval: embedding + TF-IDF + entity + LLM rerank."""
    results: list[dict] = []
    seen_ids: set[str] = set()

    def add(r: dict):
        rid = r.get("id") or r.get("document_id") or r.get("entity_id")
        if rid and rid in seen_ids:
            return
        if rid:
            seen_ids.add(rid)
        results.append(r)

    # 1. Embedding search
    emb_results = _embedding_search(query, limit=RERANK_CANDIDATES)
    for r in emb_results:
        add({**r, "source": "embedding", "final_score": r["score"]})

    # 2. TF-IDF search (only if we don't have enough from embeddings)
    if len(results) < RERANK_CANDIDATES:
        tfidf_results = _tfidf_search(query, limit=RERANK_CANDIDATES)
        for r in tfidf_results:
            add({**r, "source": "tfidf", "final_score": r["score"]})

    # 3. Entity match
    if entity_name:
        ent_results = _entity_match(entity_name)
        for r in ent_results:
            add({
                "type": "entity",
                "id": r["id"],
                "entity_id": r["id"],
                "name": r["name"],
                "entity_type": r["entity_type"],
                "score": 0.95,
                "source": "entity",
                "final_score": 0.95,
                "aliases": r.get("aliases", []),
                "confidence": r.get("confidence", 0.5),
            })

    # 4. LLM rerank the combined set
    if len(results) > 1:
        results = _rerank_with_llm(query, results)

    # Apply metadata filters
    if source_type:
        results = [r for r in results if r.get("source_type") == source_type]

    if date_from or date_to:
        filtered = []
        for r in results:
            dt_str = r.get("effective_at") or r.get("observed_at")
            if not dt_str:
                filtered.append(r)
                continue
            try:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                if date_from and dt.date() < date_from.date():
                    continue
                if date_to and dt.date() > date_to.date():
                    continue
            except ValueError:
                pass
            filtered.append(r)
        results = filtered

    return results[:limit]


# ---------------------------------------------------------------------------
# Embedding search
# ---------------------------------------------------------------------------
def _embedding_search(query: str, limit: int = 20) -> list[dict]:
    """Find chunks by embedding cosine similarity."""
    try:
        with get_session() as db:
            chunks = db.query(Chunk).all()
            if not chunks:
                return []

            chunk_texts = [c.text[:EMBEDDING_MAX_LENGTH] for c in chunks]
            doc_map = {c.document_id: c.document for c in chunks}

            query_vec = encode_single(query)
            batch_vecs = encode_batch(chunk_texts)

            # Cosine similarity (embeddings are already normalized)
            sims = batch_vecs @ query_vec  # shape (N,)

            results = []
            for idx, score in enumerate(sims):
                if float(score) < EMB_MIN_SCORE:
                    continue
                chunk = chunks[idx]
                doc = doc_map.get(chunk.document_id)
                results.append({
                    "type": "chunk",
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "score": float(score),
                    "text": chunk.text[:500],
                    "page": chunk.page,
                    "section": chunk.section,
                    "filename": doc.filename if doc else None,
                    "source_type": doc.source_type if doc else None,
                    "observed_at": chunk.metadata_json.get("observed_at") if chunk.metadata_json else None,
                    "effective_at": chunk.metadata_json.get("effective_at") if chunk.metadata_json else None,
                })

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

    except Exception as e:
        logger.warning("Embedding search failed: %s", e)
        return []


# ---------------------------------------------------------------------------
# TF-IDF search (fallback / complementary)
# ---------------------------------------------------------------------------
def _tfidf_search(query: str, limit: int = 20) -> list[dict]:
    """Fallback TF-IDF keyword search over chunks."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as sk_cosine

        with get_session() as db:
            chunks = db.query(Chunk).all()
            if not chunks:
                return []

            doc_map = {c.document_id: c.document for c in chunks}
            corpus = [c.text for c in chunks]

            vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
            try:
                matrix = vectorizer.fit_transform([query] + corpus)
            except Exception:
                return []

            sims = sk_cosine(matrix[0:1], matrix[1:]).flatten()

            results = []
            for idx, score in enumerate(sims):
                if float(score) < TFIDF_MIN_SCORE:
                    continue
                chunk = chunks[idx]
                doc = doc_map.get(chunk.document_id)
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
            return results[:limit]

    except Exception as e:
        logger.warning("TF-IDF search failed: %s", e)
        return []


# ---------------------------------------------------------------------------
# Entity exact match
# ---------------------------------------------------------------------------
def _entity_match(entity_name: str) -> list[dict]:
    """Find entities matching the name."""
    with get_session() as db:
        entities = db.query(Entity).filter(
            Entity.canonical_name.ilike(f"%{entity_name}%")
        ).all()
        return [
            {
                "id": e.id,
                "name": e.canonical_name,
                "entity_type": e.entity_type,
                "score": 0.95,
                "aliases": e.aliases_json or [],
                "confidence": e.confidence,
            }
            for e in entities
        ]


# ---------------------------------------------------------------------------
# LLM reranker
# ---------------------------------------------------------------------------
def _rerank_with_llm(query: str, results: list[dict]) -> list[dict]:
    """Re-rank results using the LLM for semantic relevance."""
    if len(results) <= 1:
        return results

    items = []
    for i, r in enumerate(results[:RERANK_CANDIDATES]):
        preview = r.get("text", "")[:150] if r.get("text") else ""
        if not preview:
            preview = f"[{r.get('type', 'unknown')}]"
        items.append(f"{i}. [{r.get('type','?')}] score={r.get('score',0):.3f}: {preview}")

    prompt = (
        f"Query: {query}\n\n"
        f"Ranked items (0-indexed):\n" + "\n".join(items) + "\n\n"
        "Return ONLY a JSON array of indices sorted by relevance to the query.\n"
        "Example: [2, 0, 5, 1, 3]"
    )

    try:
        response = chat(
            messages=[
                {"role": "system", "content": "You are a relevance ranker. Return only a JSON array of indices."},
                {"role": "user", "content": prompt},
            ],
            model="auto",
            max_tokens=500,
            timeout_s=60,
        )
        content = response["choices"][0]["message"]["content"]
        indices = json.loads(content)
        reordered = [results[i] for i in indices if isinstance(i, int) and i < len(results)]
        # Append any not mentioned
        mentioned = set(indices)
        for i, r in enumerate(results):
            if i not in mentioned:
                reordered.append(r)
        return reordered
    except Exception as e:
        logger.warning("LLM rerank failed, using original order: %s", e)
        return results
