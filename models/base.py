"""Shared helpers for model modules."""
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)
