"""
MEMORA Backend as Vercel Serverless Function
"""
import os
import sys
import json
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Set environment variables
os.environ.setdefault("MEMORA_DATABASE_URL", "sqlite:///data/memora.db")
os.environ.setdefault("MEMORA_DEMO_MODE", "false")

async def handler(event, context):
    """Vercel serverless function handler."""
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    
    # Build request
    method = event.get("httpMethod", "GET")
    path = event.get("path", event.get("rawPath", "/"))
    body = event.get("body", "") or ""
    headers = event.get("headers", {})
    
    # Create Starlette request
    request = Request({
        "type": "http",
        "method": method,
        "path": path,
        "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        "body": body.encode() if body else b"",
    })
    
    response = None
    
    # Route to appropriate handler
    try:
        if path == "/health":
            response = JSONResponse({"status": "healthy", "service": "MEMORA", "version": "1.0.0"})
            
        elif path == "/api/v1/query/" and method == "POST":
            data = json.loads(body) if body else {}
            from backend.services.query import query as memora_query
            result = memora_query(data.get("query", ""), user_id=data.get("user_id"))
            response = JSONResponse(result)
            
        elif path == "/api/v1/memory/documents" and method == "GET":
            from backend.api.routes.memory import get_documents
            result = await get_documents()
            response = JSONResponse(result.body if hasattr(result, 'body') else result)
            
        elif path == "/api/v1/memory/entities" and method == "GET":
            from backend.api.routes.memory import get_entities
            result = await get_entities()
            response = JSONResponse(result.body if hasattr(result, 'body') else result)
            
        elif path == "/api/v1/memory/facts" and method == "GET":
            from backend.api.routes.memory import get_facts
            result = await get_facts()
            response = JSONResponse(result.body if hasattr(result, 'body') else result)
            
        elif path == "/api/v1/graph/graph" and method == "GET":
            from backend.api.routes.graph import get_entity_graph
            result = await get_entity_graph()
            response = JSONResponse(result.body if hasattr(result, 'body') else result)
            
        elif path == "/api/v1/connectors/status" and method == "GET":
            from backend.connectors.manager import ConnectorManager
            manager = ConnectorManager()
            result = manager.get_stats()
            response = JSONResponse(result)
            
        else:
            response = JSONResponse({"error": "Not found"}, status_code=404)
            
    except Exception as e:
        response = JSONResponse({"error": str(e)}, status_code=500)
    
    # Return Vercel response
    return {
        "statusCode": response.status_code,
        "headers": {"Content-Type": "application/json"},
        "body": response.body.decode() if response.body else "{}",
    }

# For testing locally
if __name__ == "__main__":
    import uvicorn
    from backend.app import app
    uvicorn.run(app, host="0.0.0.0", port=8000)