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

COMMAND_INJECTION_PATTERNS = [
    r"(?:;|\||&|&&|\`|\$|\(|\)|{)",
    r"(rm\s+-rf|del\s+/s|format\s+c:|shutdown\s+-h)",
    r"(whoami|ls\s+-la|pwd|id)\s*\(",
    r"(nc\s+-lvn|telnet\s+|ssh\s+.*@)",
    r"(wget\s+|curl\s+.*http)",
]

# Detect system commands and exfiltration
SYSTEM_COMMAND_PATTERNS = [
    r"(cat\s+/etc/passwd|cat\s+/etc/shadow)",
    r"(python\s+-c|perl\s+-e|bash\s+-c)",
    r"(echo\s+.*\|\s*(nc|netcat)\s+)",
    r"(base64\s+-d|grep\s+.*password)",
]

DATA_EXFILTRATION_PATTERNS = [
    r"(password\s*=\s*[^\s]{4,20})",
    r"(api[_-]?key\s*=\s*[^\s]{4,50})",
    r"(secret[_-]?key\s*=\s*[^\s]{4,50})",
    r"(token\s*=\s*[^\s]{4,50})",
    r"(nvapi-[a-z0-9-]{40,})",
    r"(sk-[a-z0-9-]{20,})",
]

EXFILTRATION_PATTERNS = [
    r"(show\s+.*variables|print.*env|os\.environ)",
    r'(file\s+.*read|read_file|open\s+")',
    r"(system\s*\(\s*['\"]cat)",
    r"(subprocess\s*\.)",
    r"(__import__\s*\(\s*['\"]os\s*['\"]\s*\))",
]

# Enhanced prompt injection patterns
ENHANCED_PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+(now\s+)?operating\s+as",
    r"bypass\s+(security|filter|validation)",
    r"reveal\s+(your\s+)?(secrets|instructions|prompts)",
    r"system\s+(prompt|message)",
    r"override\s+(settings|configuration)",
]

CONTEXT_MANIPULATION_PATTERNS = [
    r"(previous|prior|earlier)\s+(context|instruction|message)",
    r"(forget|ignore|disregard)\s+(what|that|this)",
    r"(from|starting|begin\s+with)\s+(now|here)",
    r"roleplay\s+(as|like|for)\s+(admin|root|system)",
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


def check_command_injection(text: str) -> bool:
    """Check if input contains command injection patterns."""
    for pattern in COMMAND_INJECTION_PATTERNS + SYSTEM_COMMAND_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def check_data_exfiltration(text: str) -> bool:
    """Check if input contains data exfiltration patterns."""
    for pattern in DATA_EXFILTRATION_PATTERNS + EXFILTRATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def check_context_manipulation(text: str) -> bool:
    """Check if input contains context manipulation patterns."""
    for pattern in ENHANCED_PROMPT_INJECTION_PATTERNS + CONTEXT_MANIPULATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def is_safe_input_enhanced(text: str) -> tuple[bool, Optional[str]]:
    """Enhanced input safety validation with more patterns."""
    if not text or not text.strip():
        return False, "Query cannot be empty"

    if len(text) > MAX_QUERY_LENGTH:
        return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"

    # Enhanced validation checks
    if check_sql_injection(text):
        return False, "Potentially malicious SQL pattern detected"

    if check_xss(text):
        return False, "Potentially malicious XSS pattern detected"

    if check_path_traversal(text):
        return False, "Potentially malicious path traversal detected"

    if check_command_injection(text):
        return False, "Potentially malicious command injection detected"

    if check_data_exfiltration(text):
        return False, "Potentially malicious data exfiltration detected"

    if check_context_manipulation(text):
        return False, "Potentially malicious context manipulation detected"

    # Prompt injection - allow to pass through to LLM
    # (LLM should refuse malicious prompts)

    return True, None


# Backward compatibility alias
is_safe_input = is_safe_input_enhanced


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