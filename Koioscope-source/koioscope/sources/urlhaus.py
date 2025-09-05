from __future__ import annotations
import requests
from typing import Any, Dict
from ..config import AppConfig
from ..utils import Throttle, with_backoff

API = "https://urlhaus-api.abuse.ch/v1/payload/"

def query_hash(cfg: AppConfig, logger, h: str) -> Dict[str, Any]:
    if not cfg.urlhaus.enabled:
        return {}
    th = Throttle(cfg.urlhaus.rate_limit.requests_per_minute)
    th.wait()
    headers = {"User-Agent": "HashIntelLookup/0.2", "Accept": "application/json"}
    def do():
        resp = requests.post(API, data={"sha256_hash": h}, headers=headers, timeout=20)
        if resp.status_code in (401, 403):
            return {"error": "unauthorized"}
        if resp.status_code >= 500:
            raise RuntimeError(f"URLHaus HTTP {resp.status_code}")
        resp.raise_for_status()
        return resp.json()
    try:
        return with_backoff(do, logger=logger)
    except Exception as e:  # noqa: BLE001
        logger.warning("URLHaus query failed for %s: %s", h, e)
        return {}
