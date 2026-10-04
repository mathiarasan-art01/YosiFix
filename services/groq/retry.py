"""Retry decorators and error handling policies for Groq service."""
import time
import logging
from typing import Callable, Any, TypeVar
from functools import wraps

logger = logging.getLogger("yosifix.groq.retry")
F = TypeVar("F", bound=Callable[..., Any])

def retry_with_backoff(max_retries: int = 2, base_delay: float = 1.0, backoff_factor: float = 2.0):
    """Decorator to retry flaky API calls with exponential backoff."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        logger.warning(f"Call to {func.__name__} failed (attempt {attempt+1}/{max_retries+1}): {exc}. Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries+1} attempts failed for {func.__name__}: {exc}")
            raise last_exception
        return wrapper # type: ignore
    return decorator
