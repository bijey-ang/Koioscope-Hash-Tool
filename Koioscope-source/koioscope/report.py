from __future__ import annotations
from typing import Any, Dict, Iterable, List
import pandas as pd
import os

REPORT_COLUMNS = [
    "hash", "comment",
    "av_vendor_matches",
    "filenames",
    "pe_description", "pe_original_filename", "pe_copyright",
    "signer",
    "vt_detection_ratio",
    "first_seen", "last_seen",
    "indicator_tags",
    "source_links",
]

def write_report(rows: Iterable[Dict[str, Any]], out_path: str) -> None:
    df = pd.DataFrame(rows, columns=REPORT_COLUMNS)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if out_path.lower().endswith(".xlsx"):
        df.to_excel(out_path, index=False)
    else:
        df.to_csv(out_path, index=False, encoding="utf-8")
