"""Timestamp helper utilities."""
from datetime import datetime, timezone

def now_utc() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)

def now_iso() -> str:
    """Return ISO-8601 formatted UTC timestamp string."""
    return now_utc().isoformat()
