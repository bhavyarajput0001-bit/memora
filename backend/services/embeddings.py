"""MEMORA embedding service — local (sentence-transformers) or API-based."""
import json
import logging
import time
from typing import Optional

import numpy as np

from backend.config.embeddings import (
    EMBEDDING_BACKEND,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MAX_LENGTH,
    EMBEDDING_DIM,
    EMBEDDING_API_BASE_URL,
    EMBEDDING_API_KEY,
    EMBEDDING_API_MODEL,
    EMBEDDING_MODEL,
)

logger = logging.getLogger(__name__)

# --- Local model singleton (lazy-loaded) ---
_model = None


def _get_local_model():
    """Lazy-load the local sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s ...", EMBEDDING_MODEL)
            t0 = time.time()
            _model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
            logger.info("Embedding model loaded in %.1fs", time.time() - t0)
        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            raise
    return _model


# --- API-based client (OpenRouter / OpenAI-compatible) ---
def _encode_api(texts: list[str]) -> np.ndarray:
    """Encode texts via an OpenAI-compatible embedding API."""
    import httpx

    if not EMBEDDING_API_BASE_URL:
        raise RuntimeError("MEMORA_EMBEDDING_API_BASE_URL not set for API backend")

    all_embeddings = []
    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i : i + EMBEDDING_BATCH_SIZE]
        try:
            resp = httpx.post(
                f"{EMBEDDING_API_BASE_URL.rstrip('/')}/embeddings",
                headers={
                    "Authorization": f"Bearer {EMBEDDING_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": EMBEDDING_API_MODEL,
                    "input": batch,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", [])
            if not items:
                raise RuntimeError(f"No embeddings returned from API: {data}")
            for item in items:
                emb = item.get("embedding", [])
                arr = np.array(emb, dtype=np.float32)
                if arr.shape[0] == 0:
                    arr = np.zeros(EMBEDDING_DIM, dtype=np.float32)
                all_embeddings.append(arr)
        except Exception as e:
            logger.warning("API encode failed for batch: %s", e)
            all_embeddings.append(np.zeros(EMBEDDING_DIM, dtype=np.float32))

    return np.vstack(all_embeddings)


def encode_batch(texts: list[str]) -> np.ndarray:
    """Encode a batch of texts into vectors. Returns shape (N, dim)."""
    if not texts:
        return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

    # Truncate to model max length
    texts = [t[:EMBEDDING_MAX_LENGTH] for t in texts]

    if EMBEDDING_BACKEND == "api":
        return _encode_api(texts)

    # Local path
    model = _get_local_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def encode_single(text: str) -> np.ndarray:
    """Encode a single text. Returns shape (dim,)."""
    result = encode_batch([text])
    return result[0] if len(result) else np.zeros(EMBEDDING_DIM, dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
