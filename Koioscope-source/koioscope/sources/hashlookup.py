from __future__ import annotations
import requests
from typing import Any, Dict
from ..config import AppConfig
from ..utils import Throttle, with_backoff, detect_hash_type

BASE = "https://hashlookup.circl.lu"

def query_hash(cfg: AppConfig, logger, h: str) -> Dict[str, Any]:
    if not cfg.hashlookup.enabled:
        return {}
    th = Throttle(cfg.hashlookup.rate_limit.requests_per_minute)
    th.wait()

    htype = detect_hash_type(h) or "sha256"
    if htype not in ("md5","sha1","sha256"):
        htype = "sha256"
    url = f"{BASE}/lookup/{htype}/{h}"
    headers = {"User-Agent": "HashIntelLookup/0.2"}

    def do():
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code >= 500:
            raise RuntimeError(f"Hashlookup HTTP {resp.status_code}")
        if resp.status_code == 404:
            return {"found": False}
        resp.raise_for_status()
        return resp.json()
    try:
        return with_backoff(do, logger=logger)
    except Exception as e:  # noqa: BLE001
        logger.warning("Hashlookup query failed for %s: %s", h, e)
        return {}
