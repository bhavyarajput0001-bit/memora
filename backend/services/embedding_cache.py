"""In-memory embedding cache for MEMORA retrieval optimization.

Solves the 12-15s search latency by:
1. Loading all chunk embeddings ONCE at startup
2. Caching query results for 60 seconds
3. Incremental updates on ingest (only new chunks)
"""
import json
import logging
import time
from typing import Optional
from collections import OrderedDict

import numpy as np

from backend.db import get_session
from backend.models import Chunk
from backend.services.embeddings import encode_batch, encode_single

logger = logging.getLogger(__name__)

# Cache TTL in seconds
CACHE_TTL = 60
# Max cache size
MAX_CACHE_SIZE = 100

# Global cache state
_embedding_cache: dict[str, np.ndarray] = {}  # chunk_id -> embedding
_query_cache: OrderedDict[str, tuple[float, dict]] = OrderedDict()  # query -> (timestamp, result)
_last_ingest_time: float = 0.0
_chunk_text_cache: dict[str, str] = {}  # chunk_id -> text


def get_embedding_cache() -> dict[str, np.ndarray]:
    """Get the embedding cache."""
    return _embedding_cache


def get_chunk_text_cache() -> dict[str, str]:
    """Get the chunk text cache."""
    return _chunk_text_cache


def cache_embeddings() -> int:
    """Load all chunk embeddings into memory cache. Returns count cached."""
    global _embedding_cache, _chunk_text_cache
    
    with get_session() as db:
        chunks = db.query(Chunk).all()
    
    if not chunks:
        return 0
    
    # Load texts and existing embeddings
    texts = []
    missing_ids = []
    for chunk in chunks:
        _chunk_text_cache[chunk.id] = chunk.text
        emb = _load_embedding_from_db(chunk)
        if emb is not None:
            _embedding_cache[chunk.id] = emb
        else:
            missing_ids.append(chunk.id)
            texts.append(chunk.text[:256])
    
    # Batch encode missing embeddings
    if missing_ids and texts:
        try:
            new_embeddings = encode_batch(texts)
            for i, chunk_id in enumerate(missing_ids):
                if i < len(new_embeddings):
                    _embedding_cache[chunk_id] = new_embeddings[i]
            logger.info(f"Cached {len(_embedding_cache)} chunk embeddings")
        except Exception as e:
            logger.warning(f"Failed to cache embeddings: {e}")
    
    return len(_embedding_cache)


def _load_embedding_from_db(chunk: Chunk) -> Optional[np.ndarray]:
    """Load embedding from chunk metadata if available."""
    meta = chunk.metadata_json or {}
    emb_data = meta.get("embedding")
    if emb_data:
        try:
            if isinstance(emb_data, str):
                emb_data = json.loads(emb_data)
            return np.array(emb_data, dtype=np.float32)
        except Exception:
            pass
    return None


def add_chunk_embedding(chunk_id: str, text: str, embedding: np.ndarray) -> None:
    """Add a single chunk embedding to cache (called after ingest)."""
    _chunk_text_cache[chunk_id] = text
    _embedding_cache[chunk_id] = embedding


def clear_query_cache() -> None:
    """Clear the query result cache."""
    _query_cache.clear()


def get_cached_query(query: str) -> Optional[dict]:
    """Get a cached query result if still valid."""
    if query not in _query_cache:
        return None
    timestamp, result = _query_cache[query]
    if time.time() - timestamp > CACHE_TTL:
        del _query_cache[query]
        return None
    return result


def cache_query(query: str, result: dict) -> None:
    """Cache a query result."""
    _query_cache[query] = (time.time(), result)
    # Evict oldest if over limit
    while len(_query_cache) > MAX_CACHE_SIZE:
        _query_cache.popitem(last=False)


def get_query_embedding(query: str) -> np.ndarray:
    """Get or compute query embedding (cached)."""
    # Simple cache by query string
    cache_key = f"q:{query}"
    # For now, just compute - could add LRU cache here
    return encode_single(query)


def cosine_similarity_search(
    query_embedding: np.ndarray,
    top_k: int = 15
) -> list[tuple[str, float]]:
    """
    Fast in-memory cosine similarity search.
    Returns list of (chunk_id, score) sorted by score.
    """
    if not _embedding_cache:
        return []
    
    scores = []
    for chunk_id, emb in _embedding_cache.items():
        if len(emb) == len(query_embedding):
            sim = float(np.dot(query_embedding, emb))
            if sim >= 0.25:  # Min threshold
                scores.append((chunk_id, sim))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def rebuild_cache() -> int:
    """Rebuild the entire cache (call after significant data changes)."""
    global _embedding_cache, _chunk_text_cache
    _embedding_cache.clear()
    _chunk_text_cache.clear()
    clear_query_cache()
    return cache_embeddings()


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "cached_chunks": len(_embedding_cache),
        "cached_texts": len(_chunk_text_cache),
        "cached_queries": len(_query_cache),
        "cache_hit_rate": "N/A",  # Would need to track hits/misses
    }
