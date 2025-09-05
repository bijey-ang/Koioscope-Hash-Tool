from __future__ import annotations
import argparse, os, pandas as pd
from typing import List, Tuple, Dict, Any
from koioscope import __app_name__, __version__
from koioscope.config import load_config, AppConfig
from koioscope.logging_setup import setup_logging
from koioscope.utils import detect_hash_type, normalize_hash
from koioscope.cache import load_from_cache, save_to_cache
from koioscope.vt_client import VirusTotalClient
from koioscope.sources import urlhaus, malwarebazaar, otx, threatfox, malshare, hybrid_analysis, hashlookup
from koioscope.merge import merge_results
from koioscope.report import write_report
from tqdm import tqdm

def _load_vendor_list(path: str | None) -> List[str]:
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def _read_batch(path: str) -> List[Tuple[str, str]]:
    if path.lower().endswith(".xlsx"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    rows: List[Tuple[str, str]] = []
    for _, r in df.iterrows():
        h = str(r.get("hash","")).strip()
        c = str(r.get("comment","")).strip() if "comment" in df.columns else ""
        if h:
            rows.append((h, c))
    return rows

def process_one(cfg: AppConfig, logger, vt: VirusTotalClient, query: str, comment: str) -> Dict[str, Any]:
    if (ht := detect_hash_type(query)):
        h = normalize_hash(query)
    else:
        res = vt.search_by_filename(query)
        data = (res or {}).get("data") or []
        if data and isinstance(data, list):
            h = (data[0].get("id") or "").lower()
        else:
            h = normalize_hash(query)

    cached = load_from_cache(cfg, h)
    if cached:
        logger.info("Cache hit for %s", h)
        return cached

    vt_api = vt.fetch_file_report(h) if ht else {}
    vt_html = vt.scrape_permalink_fields(h) if ht else {}

    md5_hint = None
    try:
    	md5_hint = (((vt_api or {}).get("data") or {}).get("attributes") or {}).get("md5")
    except Exception:
    	md5_hint = None

    uh = urlhaus.query_hash(cfg, logger, h) if ht else {}
    mb = malwarebazaar.query_hash(cfg, logger, h) if ht else {}
    ms = malshare.query_hash(cfg, logger, md5_hint or h) if ht else {}
    ha = hybrid_analysis.query_hash(cfg, logger, h) if ht else {}
    hl = hashlookup.query_hash(cfg, logger, h) if ht else {}
    ox = otx.query_hash(cfg, logger, h) if ht else {}
    tf = threatfox.query_hash(cfg, logger, h) if ht else {}

    result = merge_results(h, comment, cfg.vendor_allowlist, vt_api, vt_html, uh, mb, ms, ha, hl, ox, tf)
    save_to_cache(cfg, h, result)
    return result

def main():
    ap = argparse.ArgumentParser(f"{__app_name__} CLI")
    ap.add_argument("--config", required=True, help="Path to config.yaml or .json")
    ap.add_argument("--query", help="Single hash or filename")
    ap.add_argument("--batch", help="CSV or XLSX with columns: hash[,comment]")
    ap.add_argument("--out", default="out/report.csv", help="Output CSV or XLSX")
    ap.add_argument("--vendor-list", help="Plaintext list of AV vendors to include (overrides config)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    logger = setup_logging()
    if args.vendor_list:
        cfg.vendor_allowlist = _load_vendor_list(args.vendor_list)

    vt = VirusTotalClient(cfg, logger)

    rows: List[Dict[str, Any]] = []
    if args.query:
        rows.append(process_one(cfg, logger, vt, args.query, ""))
    elif args.batch:
        for h, c in tqdm(_read_batch(args.batch), desc="Processing"):
            rows.append(process_one(cfg, logger, vt, h, c))
    else:
        ap.error("either --query or --batch is required")

    write_report(rows, args.out)
    logger.info("Wrote %s", args.out)

if __name__ == "__main__":
    main()
