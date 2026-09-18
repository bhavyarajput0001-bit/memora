"""MEMORA query API route."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services import query as query_service

router = APIRouter(prefix="/api/v1/query", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None


@router.post("/")
async def execute_query(request: QueryRequest):
    """Execute a query against the knowledge base."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = query_service.query(request.query, request.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
