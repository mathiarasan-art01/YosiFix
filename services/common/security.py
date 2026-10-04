"""Security helpers: CSRF tokens, in-memory rate limiting, safe redirects, URL validation."""
import hmac
import secrets
import threading
import time
from collections import defaultdict, deque
from functools import wraps
from urllib.parse import urlparse

from flask import abort, current_app, jsonify, request, session

CSRF_SESSION_KEY = "_csrf_token"
CSRF_EXEMPT_ENDPOINTS = {"auth.google_one_tap", "static"}


def get_csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf():
    """Called before every state-changing request."""
    if not current_app.config.get("CSRF_ENABLED", True):
        return
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    if request.endpoint in CSRF_EXEMPT_ENDPOINTS:
        return
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    expected = session.get(CSRF_SESSION_KEY, "")
    if not expected or not sent or not hmac.compare_digest(str(sent), str(expected)):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"error": "Your session expired. Refresh the page and try again."}), 400
        abort(400, description="Your session expired or the form is stale. Please refresh and try again.")
    return None


# ---------------------------------------------------------------------------
# Rate limiting (per-process sliding window; on serverless this is per instance)
# ---------------------------------------------------------------------------
_hits = defaultdict(deque)
_lock = threading.Lock()


def _client_key() -> str:
    fwd = request.headers.get("X-Forwarded-For", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.remote_addr or "unknown")
    return f"{ip}:{request.endpoint}"


def rate_limit(max_calls: int, per_seconds: int):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_app.config.get("RATELIMIT_ENABLED", True):
                key = _client_key()
                now = time.time()
                with _lock:
                    window = _hits[key]
                    while window and window[0] <= now - per_seconds:
                        window.popleft()
                    if len(window) >= max_calls:
                        retry = int(per_seconds - (now - window[0])) + 1
                        if request.path.startswith("/api/") or request.is_json:
                            resp = jsonify({"error": f"Too many requests. Try again in {retry}s."})
                            resp.status_code = 429
                            resp.headers["Retry-After"] = str(retry)
                            return resp
                        abort(429)
                    window.append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Redirect / URL safety
# ---------------------------------------------------------------------------
def is_safe_redirect(target: str) -> bool:
    """Only allow relative, same-site paths (blocks //evil.com and absolute URLs)."""
    if not target:
        return False
    parsed = urlparse(target)
    return not parsed.scheme and not parsed.netloc and target.startswith("/") and not target.startswith("//")


def safe_external_url(url: str) -> str:
    """Evidence links must be plain http(s) URLs; anything else is dropped."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return url.strip()[:600]
    return ""


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net https://accounts.google.com/gsi/client; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://accounts.google.com/gsi/style; "
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://accounts.google.com/gsi/; "
        "frame-src https://accounts.google.com/gsi/; "
        "base-uri 'self'; form-action 'self' https://accounts.google.com; frame-ancestors 'none'"
    ),
}


def apply_security_headers(response):
    for key, value in SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=3600"
    elif response.mimetype == "text/html" or request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response
