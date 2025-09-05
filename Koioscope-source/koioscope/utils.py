from __future__ import annotations
import hashlib, re, time, logging
from typing import Optional

HASH_RE = {
    "md5": re.compile(r"^[a-fA-F0-9]{32}$"),
    "sha1": re.compile(r"^[a-fA-F0-9]{40}$"),
    "sha256": re.compile(r"^[a-fA-F0-9]{64}$"),
}

def detect_hash_type(s: str) -> Optional[str]:
    x = s.strip().lower()
    for t, rx in HASH_RE.items():
        if rx.match(x):
            return t
    return None

def normalize_hash(s: str) -> str:
    return s.strip().lower()

class Throttle:
    """Simple per-service throttle based on requests/minute."""
    def __init__(self, rpm: int):
        self.interval = 60.0 / max(1, rpm)
        self.last = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last = time.time()

def with_backoff(fn, *, retries=3, base=0.5, logger: Optional[logging.Logger]=None):
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            if attempt >= retries:
                if logger:
                    logger.error("Operation failed after retries: %s", e, exc_info=True)
                raise
            sleep = base * (2 ** attempt)
            if logger:
                logger.warning("Transient error: %s; retrying in %.1fs", e, sleep)
            time.sleep(sleep)
