"""MEMORA config package — re-exports everything from config.py plus new modules."""
import os
from pathlib import Path

# Re-export all from config.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("MEMORA_DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = DATA_DIR / "uploads"
DEMO_DIR = DATA_DIR / "demo"
DB_PATH = Path(os.environ.get("MEMORA_DB_PATH", DATA_DIR / "memora.db"))

LLM_BASE_URL = os.environ.get("MEMORA_LLM_BASE_URL", "http://localhost:31416/v1")
LLM_API_KEY = os.environ.get("MEMORA_LLM_API_KEY", "local-router-key")
LLM_MODEL_FAST = os.environ.get("MEMORA_LLM_MODEL_FAST", "deepseek-v4-flash")
LLM_MODEL_STRONG = os.environ.get("MEMORA_LLM_MODEL_STRONG", "nemotron-3-ultra-550b")
LLM_MODEL_VISION = os.environ.get("MEMORA_LLM_MODEL_VISION", "auto")
LLM_TIMEOUT_S = float(os.environ.get("MEMORA_LLM_TIMEOUT_S", "60"))

EMBEDDING_ENABLED = os.environ.get("MEMORA_EMBEDDING_ENABLED", "true").lower() == "true"

MAX_FILE_SIZE_MB = int(os.environ.get("MEMORA_MAX_FILE_SIZE_MB", "50"))
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".txt", ".md",
    ".csv", ".json", ".eml", ".html", ".docx",
}

DEMO_MODE = os.environ.get("MEMORA_DEMO_MODE", "false").lower() == "true"
TRACE_ENABLED = os.environ.get("MEMORA_TRACE_ENABLED", "true").lower() == "true"
CORS_ORIGINS = os.environ.get("MEMORA_CORS_ORIGINS", "*").split(",")
HOST = os.environ.get("MEMORA_HOST", "0.0.0.0")
PORT = int(os.environ.get("MEMORA_PORT", "8000"))

# Ensure data dirs exist
for d in (DATA_DIR, UPLOAD_DIR, DEMO_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Embedding-specific config
EMBEDDING_MODEL = os.environ.get("MEMORA_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_BACKEND = os.environ.get("MEMORA_EMBEDDING_BACKEND", "local").lower()
EMBEDDING_BATCH_SIZE = int(os.environ.get("MEMORA_EMBEDDING_BATCH_SIZE", "32"))
EMBEDDING_MAX_LENGTH = int(os.environ.get("MEMORA_EMBEDDING_MAX_LENGTH", "256"))
EMBEDDING_DIM = int(os.environ.get("MEMORA_EMBEDDING_DIM", "384"))
EMBEDDING_API_BASE_URL = os.environ.get("MEMORA_EMBEDDING_API_BASE_URL", "")
EMBEDDING_API_KEY = os.environ.get("MEMORA_EMBEDDING_API_KEY", "")
EMBEDDING_API_MODEL = os.environ.get("MEMORA_EMBEDDING_API_MODEL", "text-embedding-3-small")

__all__ = [
    "BASE_DIR", "DATA_DIR", "UPLOAD_DIR", "DEMO_DIR", "DB_PATH",
    "LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL_FAST", "LLM_MODEL_STRONG",
    "LLM_MODEL_VISION", "LLM_TIMEOUT_S",
    "EMBEDDING_ENABLED", "EMBEDDING_MODEL", "EMBEDDING_BACKEND",
    "EMBEDDING_BATCH_SIZE", "EMBEDDING_MAX_LENGTH", "EMBEDDING_DIM",
    "EMBEDDING_API_BASE_URL", "EMBEDDING_API_KEY", "EMBEDDING_API_MODEL",
    "MAX_FILE_SIZE_MB", "ALLOWED_EXTENSIONS", "DEMO_MODE",
    "TRACE_ENABLED", "CORS_ORIGINS", "HOST", "PORT",
]
