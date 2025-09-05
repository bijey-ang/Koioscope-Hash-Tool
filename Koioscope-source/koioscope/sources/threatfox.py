from __future__ import annotations
import requests
from typing import Any, Dict
from ..config import AppConfig
from ..utils import Throttle, with_backoff

API = "https://threatfox-api.abuse.ch/api/v1/"

def query_hash(cfg: AppConfig, logger, h: str) -> Dict[str, Any]:
    if not cfg.threatfox.enabled:
        return {}
    th = Throttle(cfg.threatfox.rate_limit.requests_per_minute)
    th.wait()
    headers = {"User-Agent": "HashIntelLookup/0.2", "Accept": "application/json"}
    def do():
        resp = requests.post(API, json={"query": "search_hash", "hash": h}, headers=headers, timeout=20)
        if resp.status_code in (401, 403):
            return {"error": "unauthorized"}
        if resp.status_code >= 500:
            raise RuntimeError(f"ThreatFox HTTP {resp.status_code}")
        resp.raise_for_status()
        return resp.json()
    try:
        return with_backoff(do, logger=logger)
    except Exception as e:  # noqa: BLE001
        logger.warning("ThreatFox query failed for %s: %s", h, e)
        return {}
