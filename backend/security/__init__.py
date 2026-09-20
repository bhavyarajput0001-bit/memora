"""Security middleware for MEMORA - FastAPI middleware"""
import time
from typing import Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from backend.security.middleware import (
    is_safe_input,
    sanitize_input,
    sanitize_response,
    check_rate_limit,
    _request_counts,
)


class SecurityMiddleware:
    """FastAPI middleware for input validation and rate limiting."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Rate limiting
        client_ip = self._get_client_ip(request)
        rate_ok, rate_error = check_rate_limit(client_ip)
        if not rate_ok:
            return JSONResponse(
                status_code=429,
                content={"error": rate_error, "retry_after": 60}
            )
        
        # Check if this is a query endpoint that needs input validation
        path = request.url.path
        method = request.method
        
        if path == "/api/v1/query/" and method == "POST":
            # Read and validate request body
            try:
                body = await request.body()
                import json
                data = json.loads(body)
                query = data.get("query", "")
                
                # Validate input
                is_safe, error = is_safe_input(query)
                if not is_safe:
                    return JSONResponse(
                        status_code=400,
                        content={"error": error}
                    )
                
                # Sanitize input
                data["query"] = sanitize_input(query)
                
                # Create new request with sanitized body
                from starlette.datastructures import Headers, MutableHeaders
                request.headers = MutableHeaders(request.headers)
                request._body = json.dumps(data).encode()
                
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid JSON in request body"}
                )
        
        # Process request
        response = await call_next(request)
        
        # Sanitize response headers and body
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Measure processing time
        duration = time.time() - start_time
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check X-Forwarded-For header (for proxied requests)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to connection client
        scope = request.scope
        return scope.get("client", ("unknown", 0))[0]


async def security_middleware(request: Request, call_next):
    """Function-based middleware version."""
    start_time = time.time()
    
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    rate_ok, rate_error = check_rate_limit(client_ip)
    if not rate_ok:
        return JSONResponse(
            status_code=429,
            content={"error": rate_error, "retry_after": 60}
        )
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    # Measure processing time
    duration = time.time() - start_time
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    return response