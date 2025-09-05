from __future__ import annotations
import requests
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup
from .utils import Throttle, with_backoff
from .config import AppConfig

VT_API_URL = "https://www.virustotal.com/api/v3/files/"
VT_SEARCH_URL = "https://www.virustotal.com/api/v3/intelligence/search"
VT_WEB_FILE_URL = "https://www.virustotal.com/gui/file/"

class VirusTotalClient:
    def __init__(self, cfg: AppConfig, logger):
        self.api_key = cfg.virustotal.api_key
        self.throttle = Throttle(cfg.virustotal.rate_limit.requests_per_minute)
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            "x-apikey": self.api_key or "",
            "User-Agent": "HashIntelLookup/0.2",
        })

    def _get_json(self, url: str, params: Optional[dict]=None) -> Dict[str, Any]:
        self.throttle.wait()
        def do():
            resp = self.session.get(url, params=params, timeout=20)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise RuntimeError(f"VT HTTP {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        return with_backoff(do, logger=self.logger)

    def fetch_file_report(self, file_hash: str) -> Dict[str, Any]:
        url = VT_API_URL + file_hash
        try:
            data = self._get_json(url)
            return data
        except Exception as e:  # noqa: BLE001
            self.logger.warning("VT API failed for %s: %s", file_hash, e)
            return {}

    def search_by_filename(self, filename: str) -> Dict[str, Any]:
        # Best-effort: public intelligence search might be limited on free keys.
        params = {"query": f'file:{filename}', "limit": 1}
        try:
            data = self._get_json(VT_SEARCH_URL, params=params)
            return data
        except Exception as e:  # noqa: BLE001
            self.logger.warning("VT search failed for filename %s: %s", filename, e)
            return {}

    def scrape_permalink_fields(self, file_hash: str) -> Dict[str, Any]:
        """Scrape non-API fields from VT web page: signer, popular names, tags if visible."""
        url = VT_WEB_FILE_URL + file_hash
        self.throttle.wait()
        def do():
            resp = self.session.get(url, timeout=20)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise RuntimeError(f"VT web HTTP {resp.status_code}")
            resp.raise_for_status()
            return resp.text
        html = with_backoff(do, logger=self.logger)
        soup = BeautifulSoup(html, "html.parser")
        out: Dict[str, Any] = {}
        text = soup.get_text(" ", strip=True)
        for key in ["Signature", "Signer", "Authenticode"]:
            if key in text:
                out["signer_hint"] = True
                break
        if "Popular names" in text:
            out["popular_names_hint"] = True
        if "Tags" in text or "tag" in text.lower():
            out["tags_hint"] = True
        out["permalink"] = url
        return out
