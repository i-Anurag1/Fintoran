from __future__ import annotations
import time
from collections.abc import Callable


def retry_call(fn: Callable, *, attempts: int = 3, base_delay: float = 0.5):
    """Retry transient provider calls with bounded exponential backoff."""
    last = None
    for attempt in range(max(1, attempts)):
        try:
            return fn()
        except Exception as exc:
            last = exc
            if attempt + 1 >= attempts:
                raise
            time.sleep(base_delay * (2 ** attempt))
    raise last
