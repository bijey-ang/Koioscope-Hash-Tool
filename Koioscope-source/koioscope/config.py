from __future__ import annotations
import json
import yaml
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class CacheConfig:
    dir: str = "cache"
    ttl_minutes: int = 1440  # 24h

@dataclass
class RateLimit:
    requests_per_minute: int = 4

@dataclass
class ServiceConfig:
    enabled: bool = True
    api_key: Optional[str] = None
    rate_limit: RateLimit = field(default_factory=RateLimit)

@dataclass
class AppConfig:
    virustotal: ServiceConfig = field(default_factory=ServiceConfig)
    urlhaus: ServiceConfig = field(default_factory=ServiceConfig)
    malwarebazaar: ServiceConfig = field(default_factory=ServiceConfig)
    malshare: ServiceConfig = field(default_factory=ServiceConfig)
    hybrid_analysis: ServiceConfig = field(default_factory=ServiceConfig)
    hashlookup: ServiceConfig = field(default_factory=ServiceConfig)
    otx: ServiceConfig = field(default_factory=ServiceConfig)
    threatfox: ServiceConfig = field(default_factory=ServiceConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    vendor_allowlist: List[str] = field(default_factory=list)

def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        if path.lower().endswith(".json"):
            raw = json.load(f)
        else:
            raw = yaml.safe_load(f)
    def load_service(d: Dict[str, Any]) -> ServiceConfig:
        if d is None:
            return ServiceConfig()
        rl = d.get("rate_limit", {}) or {}
        return ServiceConfig(
            enabled=d.get("enabled", True),
            api_key=d.get("api_key"),
            rate_limit=RateLimit(
                requests_per_minute=int(rl.get("requests_per_minute", 4))
            )
        )
    cfg = AppConfig(
        virustotal=load_service(raw.get("virustotal", {})),
        urlhaus=load_service(raw.get("urlhaus", {})),
        malwarebazaar=load_service(raw.get("malwarebazaar", {})),
        malshare=load_service(raw.get("malshare", {})),
        hybrid_analysis=load_service(raw.get("hybrid_analysis", {})),
        hashlookup=load_service(raw.get("hashlookup", {})),
        otx=load_service(raw.get("otx", {})),
        threatfox=load_service(raw.get("threatfox", {})),
        cache=CacheConfig(**(raw.get("cache", {}) or {})),
        vendor_allowlist=[v.strip() for v in (raw.get("vendor_allowlist") or []) if v and v.strip()]
    )
    return cfg
