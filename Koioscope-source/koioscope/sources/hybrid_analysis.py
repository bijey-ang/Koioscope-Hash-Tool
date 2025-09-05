from __future__ import annotations
import requests
from typing import Any, Dict
from ..config import AppConfig
from ..utils import Throttle, with_backoff

BASE = "https://www.hybrid-analysis.com/api/v2"

def query_hash(cfg: AppConfig, logger, h: str) -> Dict[str, Any]:
    if not cfg.hybrid_analysis.enabled:
        return {}
    th = Throttle(cfg.hybrid_analysis.rate_limit.requests_per_minute)
    th.wait()

    headers = {
        "User-Agent": "Falcon Sandbox",
        "api-key": cfg.hybrid_analysis.api_key or "",
        "Accept": "application/json",
    }

    def do():
        url = f"{BASE}/search/hash"
        resp = requests.get(url, params={"hash": h}, headers=headers, timeout=25)
        if resp.status_code >= 500:
            raise RuntimeError(f"HybridAnalysis HTTP {resp.status_code}")
        if resp.status_code in (401, 403):
            return {"error": "unauthorized"}
        resp.raise_for_status()
        return resp.json()
    try:
        return with_backoff(do, logger=logger)
    except Exception as e:  # noqa: BLE001
        logger.warning("HybridAnalysis query failed for %s: %s", h, e)
        return {}
