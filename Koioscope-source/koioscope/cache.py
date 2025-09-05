from __future__ import annotations
import json, os, time
from typing import Any, Dict, Optional
from .config import AppConfig

def _path_for(cache_dir: str, h: str) -> str:
    safe = h.lower()
    return os.path.join(cache_dir, f"{safe}.json")

def load_from_cache(cfg: AppConfig, h: str) -> Optional[Dict[str, Any]]:
    os.makedirs(cfg.cache.dir, exist_ok=True)
    p = _path_for(cfg.cache.dir, h)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        ts = data.get("fetched_at", 0)
        if time.time() - ts <= cfg.cache.ttl_minutes * 60:
            return data.get("result")
        return None
    except Exception:
        return None

def save_to_cache(cfg: AppConfig, h: str, result: Dict[str, Any]) -> None:
    os.makedirs(cfg.cache.dir, exist_ok=True)
    p = _path_for(cfg.cache.dir, h)
    payload = {"fetched_at": time.time(), "result": result}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
