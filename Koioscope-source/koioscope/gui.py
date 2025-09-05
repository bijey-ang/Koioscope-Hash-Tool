from __future__ import annotations
import argparse
import os
import threading
import webbrowser
from typing import List, Dict, Any, Optional

import pandas as pd

# Tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Project imports
from koioscope import __app_name__, __version__
from koioscope.config import load_config, AppConfig
from koioscope.logging_setup import setup_logging
from koioscope.vt_client import VirusTotalClient
from koioscope.utils import detect_hash_type, normalize_hash
from koioscope.cache import load_from_cache, save_to_cache
from koioscope.sources import urlhaus, malwarebazaar, otx, threatfox, malshare, hybrid_analysis, hashlookup
from koioscope.merge import merge_results
from koioscope.report import write_report, REPORT_COLUMNS

TABLE_COLUMNS = tuple(REPORT_COLUMNS)

def process_one(cfg: AppConfig, logger, vt: VirusTotalClient, query: str, comment: str,
                vendor_list: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Single lookup: hash or filename (filename best-effort via VT search).
    Uses cache; writes to cache on success.
    """
    if (ht := detect_hash_type(query)):
        h = normalize_hash(query)
    else:
        # Best-effort filename search (public VT may be limited)
        res = vt.search_by_filename(query)
        data = (res or {}).get("data") or []
        if data and isinstance(data, list):
            h = (data[0].get("id") or "").lower()
        else:
            # If no hit, treat as raw string to keep UI responsive
            return {
                "hash": query, "comment": comment, "av_vendor_matches": "",
                "filenames": "", "pe_description": "", "pe_original_filename": "",
                "pe_copyright": "", "signer": "", "vt_detection_ratio": "",
                "first_seen": "", "last_seen": "", "indicator_tags": "",
                "source_links": ""
            }

    # Cache
    cached = load_from_cache(cfg, h)
    if cached:
        logger.info("Cache hit (GUI) for %s", h)
        return cached

    vt_api = vt.fetch_file_report(h) if ht else {}
    vt_html = vt.scrape_permalink_fields(h) if ht else {}

    md5_hint = None
    try:
    	md5_hint = (((vt_api or {}).get("data") or {}).get("attributes") or {}).get("md5")
    except Exception:
    	md5_hint = None

    uh = urlhaus.query_hash(cfg, logger, h)
    mb = malwarebazaar.query_hash(cfg, logger, h)
    ms = malshare.query_hash(cfg, logger, md5_hint or h)
    ha = hybrid_analysis.query_hash(cfg, logger, h)
    hl = hashlookup.query_hash(cfg, logger, h)
    ox = otx.query_hash(cfg, logger, h)
    tf = threatfox.query_hash(cfg, logger, h)

    vendors = vendor_list if vendor_list else cfg.vendor_allowlist
    result = merge_results(h, comment, vendors, vt_api, vt_html, uh, mb, ms, ha, hl, ox, tf)
    save_to_cache(cfg, h, result)
    return result


class HashIntelApp(ttk.Frame):
    def __init__(self, master: tk.Tk, cfg_path: str):
        super().__init__(master)
        self.master = master
        self.cfg_path = cfg_path

        # state
        self.cfg: Optional[AppConfig] = None
        self.logger = setup_logging()
        self.vendor_list_path: Optional[str] = None
        self.vendor_list: Optional[List[str]] = None
        self.vt: Optional[VirusTotalClient] = None
        self.results: List[Dict[str, Any]] = []

        self._build_ui()
        self._load_config(cfg_path)

    # ---------- UI ----------
    def _build_ui(self) -> None:
        self.master.title(f"{__app_name__} (Tkinter) v{__version__}")
        self.master.geometry("1100x620")
        self.pack(fill="both", expand=True)

        # Top: Config row
        frm_cfg = ttk.LabelFrame(self, text="Config")
        frm_cfg.pack(fill="x", padx=8, pady=6)
        ttk.Label(frm_cfg, text="Config path:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.var_cfg = tk.StringVar(value=self.cfg_path)
        self.ent_cfg = ttk.Entry(frm_cfg, textvariable=self.var_cfg)
        self.ent_cfg.grid(row=0, column=1, sticky="we", padx=6, pady=4)
        frm_cfg.columnconfigure(1, weight=1)
        ttk.Button(frm_cfg, text="Browse", command=self._browse_config).grid(row=0, column=2, padx=6, pady=4)
        ttk.Button(frm_cfg, text="Reload", command=self._reload_config).grid(row=0, column=3, padx=6, pady=4)

        # Single query row
        frm_single = ttk.LabelFrame(self, text="Single Query")
        frm_single.pack(fill="x", padx=8, pady=6)
        ttk.Label(frm_single, text="Hash / Filename:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.var_q = tk.StringVar()
        self.ent_q = ttk.Entry(frm_single, textvariable=self.var_q)
        self.ent_q.grid(row=0, column=1, sticky="we", padx=6, pady=4)
        frm_single.columnconfigure(1, weight=1)

        ttk.Label(frm_single, text="Comment:").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.var_c = tk.StringVar()
        self.ent_c = ttk.Entry(frm_single, textvariable=self.var_c, width=28)
        self.ent_c.grid(row=0, column=3, sticky="we", padx=6, pady=4)

        ttk.Button(frm_single, text="Run Single", command=self._on_run_single).grid(row=0, column=4, padx=6, pady=4)

        # Batch row
        frm_batch = ttk.LabelFrame(self, text="Batch")
        frm_batch.pack(fill="x", padx=8, pady=6)
        ttk.Label(frm_batch, text="Batch CSV/XLSX:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.var_b = tk.StringVar()
        self.ent_b = ttk.Entry(frm_batch, textvariable=self.var_b)
        self.ent_b.grid(row=0, column=1, sticky="we", padx=6, pady=4)
        frm_batch.columnconfigure(1, weight=1)

        ttk.Button(frm_batch, text="Browse", command=self._browse_batch).grid(row=0, column=2, padx=6, pady=4)
        ttk.Button(frm_batch, text="Run Batch", command=self._on_run_batch).grid(row=0, column=3, padx=6, pady=4)

        # Vendor list row
        frm_v = ttk.LabelFrame(self, text="Vendor Allowlist")
        frm_v.pack(fill="x", padx=8, pady=6)
        ttk.Label(frm_v, text="Vendors file (.txt):").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.var_v = tk.StringVar()
        self.ent_v = ttk.Entry(frm_v, textvariable=self.var_v)
        self.ent_v.grid(row=0, column=1, sticky="we", padx=6, pady=4)
        frm_v.columnconfigure(1, weight=1)

        ttk.Button(frm_v, text="Browse", command=self._browse_vendor).grid(row=0, column=2, padx=6, pady=4)
        ttk.Button(frm_v, text="Load", command=self._load_vendor_list).grid(row=0, column=3, padx=6, pady=4)

        # Buttons row
        frm_btns = ttk.Frame(self)
        frm_btns.pack(fill="x", padx=8, pady=6)
        ttk.Button(frm_btns, text="Export CSV", command=lambda: self._export("csv")).pack(side="left", padx=4)
        ttk.Button(frm_btns, text="Export XLSX", command=lambda: self._export("xlsx")).pack(side="left", padx=4)
        ttk.Button(frm_btns, text="Open Permalink", command=self._open_permalink).pack(side="left", padx=4)

        # Table
        frm_tbl = ttk.Frame(self)
        frm_tbl.pack(fill="both", expand=True, padx=8, pady=4)
        self.tree = ttk.Treeview(frm_tbl, columns=TABLE_COLUMNS, show="headings", selectmode="browse")
        for col in TABLE_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160 if col != "indicator_tags" else 220, stretch=True)
        vsb = ttk.Scrollbar(frm_tbl, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_tbl, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frm_tbl.rowconfigure(0, weight=1)
        frm_tbl.columnconfigure(0, weight=1)

        # Status bar
        self.var_status = tk.StringVar(value="Ready")
        lbl_status = ttk.Label(self, textvariable=self.var_status, anchor="w", relief="sunken")
        lbl_status.pack(fill="x", padx=0, pady=0, ipady=3)

    # ---------- helpers ----------
    def _set_status(self, s: str) -> None:
        self.var_status.set(s)
        self.update_idletasks()

    def _browse_config(self) -> None:
        p = filedialog.askopenfilename(title="Select config.yaml or .json",
                                       filetypes=[("YAML/JSON", "*.yaml *.yml *.json"), ("All Files", "*.*")])
        if p:
            self.var_cfg.set(p)

    def _reload_config(self) -> None:
        path = self.var_cfg.get().strip()
        if not path:
            messagebox.showerror("Config", "Please select a config file.")
            return
        self._load_config(path)

    def _load_config(self, p: str) -> None:
        try:
            self.cfg = load_config(p)
            self.vt = VirusTotalClient(self.cfg, self.logger)
            self._set_status(f"Config loaded: {os.path.basename(p)}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Config", f"Failed to load config: {e}")

    def _browse_batch(self) -> None:
        p = filedialog.askopenfilename(title="Choose batch CSV/XLSX",
                                       filetypes=[("CSV/XLSX", "*.csv *.xlsx"), ("All Files", "*.*")])
        if p:
            self.var_b.set(p)

    def _browse_vendor(self) -> None:
        p = filedialog.askopenfilename(title="Choose vendor allowlist (.txt)",
                                       filetypes=[("Text", "*.txt"), ("All Files", "*.*")])
        if p:
            self.var_v.set(p)

    def _load_vendor_list(self) -> None:
        p = self.var_v.get().strip()
        if not p:
            messagebox.showwarning("Vendor list", "Please choose a .txt file first.")
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                self.vendor_list = [ln.strip() for ln in f if ln.strip()]
            self.vendor_list_path = p
            self._set_status(f"Loaded {len(self.vendor_list)} vendors.")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Vendor list", f"Failed to load: {e}")

    def _export(self, kind: str) -> None:
        if not self.results:
            messagebox.showinfo("Export", "No results to export.")
            return
        if kind == "csv":
            p = filedialog.asksaveasfilename(title="Save CSV", defaultextension=".csv",
                                             filetypes=[("CSV", "*.csv")])
        else:
            p = filedialog.asksaveasfilename(title="Save XLSX", defaultextension=".xlsx",
                                             filetypes=[("Excel", "*.xlsx")])
        if not p:
            return
        try:
            write_report(self.results, p)
            self._set_status(f"Saved {p}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Export", f"Failed: {e}")

    def _add_table_row(self, res: Dict[str, Any]) -> None:
        vals = tuple(res.get(col, "") for col in TABLE_COLUMNS)
        self.tree.insert("", "end", values=vals)

    def _open_permalink(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Open Permalink", "Select a row first.")
            return
        idx = self.tree.index(sel[0])
        if idx < 0 or idx >= len(self.results):
            return
        links = self.results[idx].get("source_links","")
        if not links:
            messagebox.showinfo("Open Permalink", "No link found for this row.")
            return
        first = links.split(";")[0].strip()
        if first:
            webbrowser.open(first)

    # ---------- run actions ----------
    def _on_run_single(self) -> None:
        q = self.var_q.get().strip()
        c = self.var_c.get().strip()
        if not q:
            messagebox.showwarning("Single", "Enter a hash or filename.")
            return
        if not self.cfg or not self.vt:
            messagebox.showerror("Config", "Load a valid config first.")
            return
        self._set_status("Running single...")
        t = threading.Thread(target=self._run_single_worker, args=(q, c), daemon=True)
        t.start()

    def _run_single_worker(self, q: str, c: str) -> None:
        try:
            res = process_one(self.cfg, self.logger, self.vt, q, c, self.vendor_list)
            self.results.append(res)
            self.after(0, lambda: self._add_table_row(res))
            self.after(0, lambda: self._set_status("Done"))
        except Exception as e:  # noqa: BLE001
            self.after(0, lambda: messagebox.showerror("Run Single", f"Error: {e}"))
            self.after(0, lambda: self._set_status("Error"))

    def _on_run_batch(self) -> None:
        p = self.var_b.get().strip()
        if not p:
            messagebox.showwarning("Batch", "Choose a CSV/XLSX file.")
            return
        if not os.path.exists(p):
            messagebox.showerror("Batch", f"File not found: {p}")
            return
        if not self.cfg or not self.vt:
            messagebox.showerror("Config", "Load a valid config first.")
            return
        self._set_status("Running batch...")
        t = threading.Thread(target=self._run_batch_worker, args=(p,), daemon=True)
        t.start()

    def _run_batch_worker(self, path: str) -> None:
        try:
            if path.lower().endswith(".xlsx"):
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)
            count = 0
            for _, r in df.iterrows():
                h = str(r.get("hash","")).strip()
                c = str(r.get("comment","")).strip() if "comment" in df.columns else ""
                if not h:
                    continue
                res = process_one(self.cfg, self.logger, self.vt, h, c, self.vendor_list)
                self.results.append(res)
                self.after(0, lambda rr=res: self._add_table_row(rr))
                count += 1
            self.after(0, lambda: self._set_status(f"Batch done ({count} items)"))
        except Exception as e:  # noqa: BLE001
            self.after(0, lambda: messagebox.showerror("Run Batch", f"Error: {e}"))
            self.after(0, lambda: self._set_status("Error"))


def main() -> None:
    ap = argparse.ArgumentParser("Hash Intel Lookup (Tkinter GUI)")
    ap.add_argument("--config", required=True, help="Path to config.yaml or .json")
    args = ap.parse_args()

    root = tk.Tk()
    app = HashIntelApp(root, args.config)
    app.mainloop()


if __name__ == "__main__":
    main()
