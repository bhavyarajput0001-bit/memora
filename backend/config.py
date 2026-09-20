"""MEMORA configuration -- all settings from environment variables with safe defaults."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("MEMORA_DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = DATA_DIR / "uploads"
DEMO_DIR = DATA_DIR / "demo"
DB_PATH = Path(os.environ.get("MEMORA_DB_PATH", DATA_DIR / "memora.db"))

# LLM router (NVIDIA NIM API - Nemotron models)
LLM_BASE_URL = os.environ.get("MEMORA_LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")
LLM_API_KEY = os.environ.get("MEMORA_LLM_API_KEY", "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")
LLM_MODEL_FAST = os.environ.get("MEMORA_LLM_MODEL_FAST", "nvidia/nemotron-3-ultra-550b-a55b")
LLM_MODEL_STRONG = os.environ.get("MEMORA_LLM_MODEL_STRONG", "nvidia/nemotron-3-ultra-550b-a55b")
LLM_MODEL_VISION = os.environ.get("MEMORA_LLM_MODEL_VISION", "nvidia/llama-3.2-11b-vision-instruct")
LLM_TIMEOUT_S = float(os.environ.get("MEMORA_LLM_TIMEOUT_S", "120"))

# Embeddings: local sentence-transformers or external API
EMBEDDING_ENABLED = os.environ.get("MEMORA_EMBEDDING_ENABLED", "true").lower() == "true"

# File limits
MAX_FILE_SIZE_MB = int(os.environ.get("MEMORA_MAX_FILE_SIZE_MB", "50"))
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".txt", ".md",
    ".csv", ".json", ".eml", ".html", ".docx",
}

# Demo mode
DEMO_MODE = os.environ.get("MEMORA_DEMO_MODE", "false").lower() == "true"

# Tracing
TRACE_ENABLED = os.environ.get("MEMORA_TRACE_ENABLED", "true").lower() == "true"

# CORS
CORS_ORIGINS = os.environ.get("MEMORA_CORS_ORIGINS", "*").split(",")

# Server
HOST = os.environ.get("MEMORA_HOST", "0.0.0.0")
PORT = int(os.environ.get("MEMORA_PORT", "8000"))

# Ensure data dirs exist
for d in (DATA_DIR, UPLOAD_DIR, DEMO_DIR):
    d.mkdir(parents=True, exist_ok=True)
