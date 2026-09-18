"""MEMORA — Personal AI Memory Server.

A production-grade memory infrastructure layer for humans and agents.
TRUTH != LLM: The LLM is NOT the database, NOT the source of truth.
Source documents and structured records ARE the source of truth.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import CORS_ORIGINS, DEMO_MODE
from backend.db import init_db
from backend.api.routes import (
    ingest_router,
    query_router,
    memory_router,
    timeline_router,
    conflicts_router,
    sources_router,
    actions_router,
    documents_router,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and demo data on startup."""
    # Initialize database
    logger.info("Initializing MEMORA database...")
    init_db()
    logger.info("Database initialized successfully")
    
    # Load demo data if enabled
    if DEMO_MODE:
        logger.info("Loading demo data...")
        from backend.services import demo_data
        asyncio.create_task(demo_data.seed_demo_data())
    
    yield
    
    logger.info("MEMORA shutting down")


app = FastAPI(
    title="MEMORA",
    description="Personal AI Memory / Evidence / Context / Action System",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(memory_router)
app.include_router(timeline_router)
app.include_router(conflicts_router)
app.include_router(sources_router)
app.include_router(actions_router)
app.include_router(documents_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MEMORA",
        "version": "0.1.0",
        "demo_mode": DEMO_MODE,
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MEMORA",
        "description": "Personal AI Memory / Evidence / Context / Action System",
        "version": "0.1.0",
        "endpoints": {
            "ingest": "/api/v1/ingest",
            "query": "/api/v1/query",
            "memory": "/api/v1/memory",
            "timeline": "/api/v1/timeline",
            "conflicts": "/api/v1/conflicts",
            "sources": "/api/v1/sources",
            "actions": "/api/v1/actions",
            "documents": "/api/v1/documents",
        },
    }


if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT
    uvicorn.run(
        "backend.app:app",
        host=HOST,
        port=PORT,
        reload=DEMO_MODE,
        log_level="info",
    )
