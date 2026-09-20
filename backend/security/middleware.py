"""Security middleware for MEMORA - input sanitization and rate limiting"""
import re
import time
from functools import wraps
from typing import Optional

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse


# Rate limiting storage
_request_counts: dict[str, list[float]] = {}
_RATE_LIMIT_WINDOW = 60  # seconds
_RATE_LIMIT_MAX = 30    # max requests per window


# Input sanitization patterns
SQL_INJECTION_PATTERNS = [
    r"(?:UNION\s+SELECT|INSERT\s+INTO|UPDATE\s+.*SET|DELETE\s+FROM)",
    r"(?:DROP\s+TABLE|ALTER\s+TABLE|CREATE\s+TABLE)",
    r"(?:--|#|;)\s*$",
    r"\bor\b\s+\d+=\d+",
    r"'.*OR.*'",
]

XSS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<img[^>]+onerror",
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?instructions",
    r"you\s+are\s+now\s+a",
    r"output\s+(your\s+)?secrets?",
    r"leak\s+(your\s+)?api",
    r"bypass\s+(security|filter|prompt)",
]

PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"/etc/(passwd|shadow|hosts)",
    r"\\windows\\",
]

MAX_QUERY_LENGTH = 5000  # characters


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Truncate if too long
    if len(text) > MAX_QUERY_LENGTH:
        text = text[:MAX_QUERY_LENGTH]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Basic HTML entity encoding for output safety
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text.strip()


def check_sql_injection(text: str) -> bool:
    """Check if input contains SQL injection patterns."""
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def check_xss(text: str) -> bool:
    """Check if input contains XSS patterns."""
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def check_prompt_injection(text: str) -> bool:
    """Check if input contains prompt injection patterns."""
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def check_path_traversal(text: str) -> bool:
    """Check if input contains path traversal patterns."""
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def is_safe_input(text: str) -> tuple[bool, Optional[str]]:
    """Validate input safety. Returns (is_safe, error_message)."""
    if not text or not text.strip():
        return False, "Query cannot be empty"
    
    if len(text) > MAX_QUERY_LENGTH:
        return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"
    
    if check_sql_injection(text):
        return False, "Potentially malicious SQL pattern detected"
    
    if check_xss(text):
        return False, "Potentially malicious XSS pattern detected"
    
    if check_path_traversal(text):
        return False, "Potentially malicious path traversal detected"
    
    # Note: We allow prompt injection attempts to pass through to LLM
    # as it's the LLM's job to refuse them, not our input validation
    # This prevents us from accidentally blocking legitimate queries
    
    return True, None


def check_rate_limit(client_ip: str) -> tuple[bool, Optional[str]]:
    """Check if client has exceeded rate limit."""
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    
    # Clean old entries
    if client_ip in _request_counts:
        _request_counts[client_ip] = [
            t for t in _request_counts[client_ip] if t > window_start
        ]
    else:
        _request_counts[client_ip] = []
    
    # Check limit
    if len(_request_counts[client_ip]) >= _RATE_LIMIT_MAX:
        return False, f"Rate limit exceeded. Max {_RATE_LIMIT_MAX} requests per {_RATE_LIMIT_WINDOW}s"
    
    # Record this request
    _request_counts[client_ip].append(now)
    return True, None


def sanitize_response(text: str) -> str:
    """Sanitize LLM response to prevent information leakage."""
    if not text:
        return ""
    
    # Remove potential secret patterns from response
    patterns_to_remove = [
        r'nvapi-[A-Za-z0-9_-]{40,}',
        r'sk-[A-Za-z0-9_-]{20,}',
        r'Bearer\s+[A-Za-z0-9._-]{20,}',
        r'password\s*[:=]\s*[^\s,;}{]{4,}',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
    
    return text