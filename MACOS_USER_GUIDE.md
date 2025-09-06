# Koioscope — macOS End‑User Handbook (Portable ZIP)

This guide is for **non‑developers on macOS** using the **portable Koioscope bundle**. No admin rights, Python, or Homebrew required.

---

## 1) System requirements

- **macOS**: 12 Monterey or newer (Intel or Apple Silicon).  
- **CPU/Build match**: Use the ZIP for your Mac:
  - Apple Silicon (M1/M2/M3) → `Koioscope-macOS-arm64-portable.zip`
  - Intel Mac → `Koioscope-macOS-x86_64-portable.zip`
- **Network access** to:
  - `www.virustotal.com`, `otx.alienvault.com`, `urlhaus.abuse.ch`, `bazaar.abuse.ch`, `threatfox.abuse.ch`  
  - `malshare.com`, `www.hybrid-analysis.com`, `hashlookup.circl.lu`
- **Disk space**: ~300–600 MB for the unpacked folder, plus room for cache and reports.
- **No administrator privileges required.** Everything runs from your home folder.

---

## 2) What you downloaded

A file named like **`Koioscope-macOS-<arch>-portable.zip`**.  
After extracting, you should see a folder **`Koioscope/`** with at least:

```
Koioscope/
  Koioscope-GUI.app          # GUI application bundle
  Koioscope-GUI.command      # Double-click launcher (passes config)
  cli/koioscope              # CLI executable (do not move)
  Koioscope-CLI.command      # CLI launcher (double-click or Terminal)
  config.yaml                # Your editable settings (API keys, rate limits, proxy, cache)
  README.md
  samples/                   # Sample CSV/XLSX, vendor allowlist, config template
  _internal/ …               # Runtime files (do not delete/move)
```

> **Keep all files together** inside the `Koioscope` folder. Do **not** drag the app out of this folder.

---

## 3) Extract the ZIP

### Option A — Finder (recommended)
1. **Double‑click** the ZIP → macOS creates a `Koioscope/` folder in the same location.
2. **Move** the whole `Koioscope` folder somewhere convenient (e.g., `~/Applications/Koioscope` or `~/Documents/Koioscope`).

### Option B — Terminal
```bash
unzip ~/Downloads/Koioscope-macOS-<arch>-portable.zip -d ~/Applications
open ~/Applications/Koioscope
```

> If macOS shows the file as “quarantined” later (Gatekeeper warning), see **§8 Gatekeeper & first‑run**.

---

## 4) First‑time setup — edit `config.yaml`

1. Open the `Koioscope` folder.  
2. **Right‑click `config.yaml` → Open With → TextEdit** (or your editor).  
3. Fill in API keys and settings. Typical example:

```yaml
virustotal:
  enabled: true
  api_key: "<YOUR_VT_PUBLIC_KEY>"
  rate_limit: { requests_per_minute: 4 }

malwarebazaar:
  enabled: true
  api_key: "<YOUR_MALWAREBAZAAR_AUTH_KEY>"   # if you have one
  rate_limit: { requests_per_minute: 10 }

malshare:
  enabled: true
  api_key: "<YOUR_MALSHARE_API_KEY>"
  rate_limit: { requests_per_minute: 10 }

hybrid_analysis:
  enabled: true
  api_key: "<YOUR_HYBRID_ANALYSIS_API_KEY>"
  rate_limit: { requests_per_minute: 5 }

hashlookup:
  enabled: true
  rate_limit: { requests_per_minute: 20 }

urlhaus:   { enabled: true, rate_limit: { requests_per_minute: 10 } }
otx:       { enabled: true, api_key: "", rate_limit: { requests_per_minute: 10 } }
threatfox: { enabled: true, rate_limit: { requests_per_minute: 10 } }

# macOS user-writable defaults (recommended)
cache: { dir: "~/Library/Application Support/Koioscope/cache", ttl_minutes: 1440 }

# Optional enterprise proxy
# http_proxy:  "http://user:pass@proxy.company.com:8080"
# https_proxy: "http://user:pass@proxy.company.com:8080"
```
4. **Save** the file and close the editor.

> To restrict which AV vendors appear in reports, use a **vendor allowlist** (one vendor per line). A sample is in `samples/vendor_allowlist.txt` (set it from the GUI/CLI when exporting).

---

## 5) Launch the GUI (recommended for ad‑hoc checks)

From Finder: **double‑click** `Koioscope-GUI.command`.  
- If nothing opens, see **§8 Gatekeeper & first‑run**.
- If you see a permission dialog, click **Open**.

### Using the GUI
- **Single lookup**: Enter a hash (MD5/SHA1/SHA256) or filename → optional comment → **Run Single**.  
- **Batch lookup**: Click **Run Batch** and choose a CSV/XLSX file.
  - CSV columns: `hash, comment` (comment optional)
  - XLSX: first sheet with the same column names
- **Export**: Use **Export CSV** or **Export XLSX** to save a report. The schema is fixed:
  ```
  hash, comment, av_vendor_matches, filenames,
  pe_description, pe_original_filename, pe_copyright,
  signer, vt_detection_ratio, first_seen, last_seen,
  indicator_tags, source_links
  ```
- **Open Permalink**: Select a row and click **Open Permalink** to open VirusTotal in your browser.
- **Status/errors**: shown at the bottom of the window.

---

## 6) Run the CLI (for automation / servers)

### Option A — Double‑click launcher, then choose inputs as prompted  
Double‑click `Koioscope-CLI.command` and follow prompts (if any).

### Option B — Terminal (flexible)
Open **Terminal** in the `Koioscope` folder and run:

```bash
# Single hash → prints details; use --out to save
./Koioscope-CLI.command --query 44d88612fea8a8f36de82e1278abb02f

# Batch from CSV → CSV report
./Koioscope-CLI.command --batch samples/sample_batch.csv --out out/batch_report.csv

# Batch from XLSX → XLSX report
./Koioscope-CLI.command --batch samples/sample_batch.xlsx --out out/batch_report.xlsx

# With an AV vendor allowlist
./Koioscope-CLI.command --batch samples/sample_batch.csv \
  --vendor-list samples/vendor_allowlist.txt \
  --out out/report.csv
```

> If you prefer to run the underlying binary directly (not the `.command` wrapper), pass `--config "$(pwd)/config.yaml"` yourself.

---

## 7) Hash behavior & sources (quick notes)

- Hash types (MD5/SHA1/SHA256) are auto‑detected and normalized.
- **MalShare** accepts **MD5 only** → Koioscope resolves MD5 from VirusTotal when only SHA‑256 is known.
- **URLHaus** uses **SHA‑256** primarily.
- Other sources accept multiple hash types.
- Results are cached locally and reused according to `ttl_minutes` in `config.yaml`.

---

## 8) Gatekeeper & first‑run (Important)

Depending on how your organization distributes apps, you may see one of the following when launching for the first time:

### A) “App is from an unidentified developer”
1. **Right‑click** `Koioscope-GUI.command` → **Open** → **Open**.  
   (This whitelists it for future runs.)

### B) “Koioscope-GUI.app” cannot be opened / is damaged
Some downloads are marked as **quarantined**. Remove quarantine attributes:
```bash
# Run inside the Koioscope folder
xattr -dr com.apple.quarantine .
```
Then try launching again.

### C) “Permission denied” for `.command`
Make launchers executable:
```bash
chmod +x Koioscope-GUI.command Koioscope-CLI.command
```

If your Mac is **corporate‑managed**, check with your IT team if additional approvals are required.

---

## 9) Where things are stored

- **Logs** (for troubleshooting):  
  `~/Library/Logs/Koioscope/run.jsonl`  
  Show the last lines:
  ```bash
  tail -n 50 ~/Library/Logs/Koioscope/run.jsonl
  ```

- **Cache** (safe to delete to force fresh lookups):  
  `~/Library/Application Support/Koioscope/cache`  
  Clear it (optional):
  ```bash
  rm -rf ~/Library/Application\ Support/Koioscope/cache/*
  ```

- **Reports**: Wherever you save them (e.g., `~/Documents/Koioscope/out`).

---

## 10) Updating Koioscope

1. Quit Koioscope.  
2. Delete the **old** `Koioscope/` folder.  
3. Extract the **new** `Koioscope-macOS-<arch>-portable.zip`.  
4. Copy your previous `config.yaml` into the new folder (overwrite).

> Do not copy `_internal/` or mix files between versions.

---

## 11) Troubleshooting

- **Network/401/403 errors** → API key missing or invalid. Edit `config.yaml`.  
- **429 (rate limit)** → Lower the per‑source `requests_per_minute` in `config.yaml`, or wait and retry.  
- **Proxy required** → Add `http_proxy` / `https_proxy` in `config.yaml` or export env vars before launching.  
- **Report won’t save** → Choose a writable folder and ensure the file ends with `.csv` or `.xlsx`.  
- **Batch file errors** → Confirm CSV header `hash, comment` (comment optional). In XLSX, use the first sheet with those columns.
- **Nothing happens on double‑click** → Open Terminal in the folder and run:
  ```bash
  ./Koioscope-GUI.command
  ```

---

## 12) Quick reference (copy‑paste)

```bash
# Move to Applications and open folder
mv ~/Downloads/Koioscope ~/Applications/Koioscope
open ~/Applications/Koioscope

# First-run: remove quarantine if blocked
cd ~/Applications/Koioscope
xattr -dr com.apple.quarantine .
chmod +x Koioscope-GUI.command Koioscope-CLI.command

# Edit config
open -e config.yaml

# GUI
./Koioscope-GUI.command

# CLI
./Koioscope-CLI.command --batch samples/sample_batch.csv --out out.csv

# View logs
tail -n 50 ~/Library/Logs/Koioscope/run.jsonl
```

---

## 13) Getting help

When asking for help, include:
- The last ~50 lines of `~/Library/Logs/Koioscope/run.jsonl`
- Your `config.yaml` (**remove API keys** before sharing)
- What you clicked or the exact CLI command you ran
- A sample of the file you tested (if batch)

Koioscope should now be ready on your Mac. Happy hunting! 🔎
