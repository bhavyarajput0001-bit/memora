"""MEMORA API routes package."""
from backend.api.routes.ingest import router as ingest_router
from backend.api.routes.query import router as query_router
from backend.api.routes.memory import router as memory_router
from backend.api.routes.timeline import router as timeline_router
from backend.api.routes.conflicts import router as conflicts_router
from backend.api.routes.sources import router as sources_router
from backend.api.routes.actions import router as actions_router
from backend.api.routes.documents import router as documents_router
from backend.api.routes.connectors import router as connectors_router
from backend.api.routes.graph import router as graph_router

__all__ = [
    "ingest_router",
    "query_router",
    "memory_router",
    "timeline_router",
    "conflicts_router",
    "sources_router",
    "actions_router",
    "documents_router",
    "connectors_router",
    "graph_router",
]
