from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

def get_identifier(request: Request) -> str:
    """
    Extracts rate limit key:
    Uses session_id cookie if available, otherwise falls back to client IP address.
    """
    session_id = request.cookies.get("session_id")
    if session_id:
        return f"session:{session_id}"
    ip = get_remote_address(request)
    return f"ip:{ip or '127.0.0.1'}"

limiter = Limiter(key_func=get_identifier)
