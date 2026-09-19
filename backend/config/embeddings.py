"""Embedding configuration for MEMORA."""
import os

# Model selection
EMBEDDING_MODEL = os.environ.get(
    "MEMORA_EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",  # 22M params, 384-dim, fast on CPU/MPS
)

# Backend options: "local" (sentence-transformers) or "api" (OpenRouter/other)
EMBEDDING_BACKEND = os.environ.get("MEMORA_EMBEDDING_BACKEND", "local").lower()

# API-based embedding config
EMBEDDING_API_BASE_URL = os.environ.get("MEMORA_EMBEDDING_API_BASE_URL", "")
EMBEDDING_API_KEY = os.environ.get("MEMORA_EMBEDDING_API_KEY", "")
EMBEDDING_API_MODEL = os.environ.get("MEMORA_EMBEDDING_API_MODEL", "text-embedding-3-small")

# Batch size for encoding
EMBEDDING_BATCH_SIZE = int(os.environ.get("MEMORA_EMBEDDING_BATCH_SIZE", "32"))

# Max text length for encoding (model-dependent; MiniLM = 256)
EMBEDDING_MAX_LENGTH = int(os.environ.get("MEMORA_EMBEDDING_MAX_LENGTH", "256"))

# Dimension of the embedding model
EMBEDDING_DIM = {
    "all-MiniLM-L6-v2": 384,
    "all-MiniLM-L12-v2": 384,
    "paraphrase-multilingual-MiniLM-L12-v2": 384,
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}.get(EMBEDDING_MODEL, 384)
