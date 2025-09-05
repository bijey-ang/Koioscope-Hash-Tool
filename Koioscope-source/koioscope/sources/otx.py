from __future__ import annotations
import requests
from typing import Any, Dict
from ..config import AppConfig
from ..utils import Throttle, with_backoff

BASE = "https://otx.alienvault.com/api/v1/indicators/file/"

def query_hash(cfg: AppConfig, logger, h: str) -> Dict[str, Any]:
    if not cfg.otx.enabled:
        return {}
    th = Throttle(cfg.otx.rate_limit.requests_per_minute)
    th.wait()
    headers = {"User-Agent":"HashIntelLookup/0.2"}
    if cfg.otx.api_key:
        headers["X-OTX-API-KEY"] = cfg.otx.api_key
    def do():
        resp = requests.get(BASE + h + "/general", headers=headers, timeout=20)
        if resp.status_code >= 500:
            raise RuntimeError(f"OTX HTTP {resp.status_code}")
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        return resp.json()
    try:
        return with_backoff(do, logger=logger)
    except Exception as e:  # noqa: BLE001
        logger.warning("OTX query failed for %s: %s", h, e)
        return {}
