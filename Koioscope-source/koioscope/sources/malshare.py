from __future__ import annotations
import requests
from typing import Any, Dict
from ..config import AppConfig
from ..utils import Throttle, with_backoff

API = "https://malshare.com/api.php"

def query_hash(cfg: AppConfig, logger, h: str) -> Dict[str, Any]:
    if not cfg.malshare.enabled:
        return {}
    th = Throttle(cfg.malshare.rate_limit.requests_per_minute)
    th.wait()

    params = {"api_key": cfg.malshare.api_key or "", "action": "details", "hash": h}
    headers = {"User-Agent": "HashIntelLookup/0.2"}

    def do():
        resp = requests.get(API, params=params, headers=headers, timeout=20)
        if resp.status_code >= 500:
            raise RuntimeError(f"MalShare HTTP {resp.status_code}")
        if resp.status_code == 403:
            return {"error": "forbidden"}
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"raw": resp.text}
    try:
        return with_backoff(do, logger=logger)
    except Exception as e:  # noqa: BLE001
        logger.warning("MalShare query failed for %s: %s", h, e)
        return {}
