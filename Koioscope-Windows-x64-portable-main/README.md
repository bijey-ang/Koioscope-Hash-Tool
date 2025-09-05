# Koioscope

An online hash/filename checker that queries VirusTotal (public API) and other permanently-free threat intel services.
Provides both a minimal cross-platform GUI and a CLI.

## Features

- Inputs:
  - Mode A: single query (hash or filename).
  - Mode B: batch from CSV/XLSX (columns: `hash[, comment]`).
  - Hash types auto-detected/normalized: MD5, SHA1, SHA256.
  - Config (YAML/JSON): API keys, vendor allowlist, rate limits, cache TTL.
- Core:
  1. VirusTotal API JSON + VT permalink HTML parsing (for fields missing in API).
  2. Queries extra free sources (URLHaus, MalwareBazaar, OTX-free, ThreatFox, **MalShare, Hybrid Analysis, CIRCL Hashlookup**) and merges results.
  3. Caching: per-hash JSON cache with TTL and reuse on repeats.
  4. Reports: generate CSV and XLSX with a fixed schema.
- GUI:
  - PySimpleGUI-based: input box, file picker, vendor list loader, Run, progress, results table,
    Export CSV/XLSX, open permalink, status/errors.
- Engineering:
  - Only free/open-source libs; respects rate limits; retries/backoff/timeouts.
  - Cross-platform (Windows/macOS/Linux), Python ≥ 3.10.
  - Robust validation/error handling; structured logging (console + JSONL).
  - Clean module layout, type hints, unit tests for parsing/normalization/merging.

## Install (Windows/macOS/Linux)

1) **Install Python 3.10+**  
   - Windows: https://www.python.org/downloads/windows/ (check “Add Python to PATH”)
   - macOS: `brew install python@3.11` (or use python.org installer)
   - Linux (Debian/Ubuntu): `sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv`

2) **Create and activate a virtual env** (recommended)
```bash
python -m venv .venv
# Windows PowerShell:
. .venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

3) **Install dependencies**
```bash
pip install -r requirements.txt
```

4) **Configure API keys & settings**  
   Copy `samples/sample_config_extended.yaml` to `config.yaml` and edit:
- `virustotal.api_key`: your VT public API key (free tier is OK).
- Optional service toggles and rate limits.
- `vendor_allowlist`: list of AV vendors to include in the report.
- `cache.ttl_minutes`: cache TTL per hash.

> **Rate-limit notes (typical)**  
> - VirusTotal public: ~4 requests/minute (check your account limits).  
> - MalwareBazaar/URLHaus/ThreatFox: Free public APIs; keep low RPS.  
> - OTX (AlienVault): API key is free; respect limits.  
> - MalShare: requires an API key.  
> - Hybrid Analysis: requires an API key, use low RPM.  
> - Hashlookup (CIRCL): no key needed.  
> Configure `rate_limits` in `config.yaml` accordingly.

## Run (CLI)

Single query:
```bash
python -m hash_intel_lookup.cli --config config.yaml --query 44d88612fea8a8f36de82e1278abb02f
```

Batch from CSV/XLSX (columns: `hash[,comment]`):
```bash
python -m hash_intel_lookup.cli --config config.yaml --batch samples/sample_batch.csv --out out/report.csv
python -m hash_intel_lookup.cli --config config.yaml --batch samples/sample_batch.xlsx --out out/report.xlsx
```

Use a vendor allowlist file (plain text, one vendor per line):
```bash
python -m hash_intel_lookup.cli --config config.yaml --batch samples/sample_batch.csv --vendor-list samples/vendor_allowlist.txt
```

## Run (GUI)

```bash
python -m hash_intel_lookup.gui --config config.yaml
```
Then interactively select a hash or a batch file and export CSV/XLSX.

## Project Layout

```
hash_intel_lookup/
  __init__.py
  cache.py
  cli.py
  config.py
  gui.py
  logging_setup.py
  merge.py
  report.py
  utils.py
  vt_client.py
  sources/
    __init__.py
    malwarebazaar.py
    malshare.py
    hybrid_analysis.py
    hashlookup.py
    otx.py
    threatfox.py
    urlhaus.py
samples/
  sample_config.yaml
  sample_config_extended.yaml
  sample_config_with_user_keys.yaml
  sample_config.json
  sample_batch.csv
  sample_batch.xlsx
  vendor_allowlist.txt
tests/
  test_utils.py
  test_merge.py
  test_parsers.py
requirements.txt
```

## Additional sources added
- MalShare (API key required) — set under `malshare.api_key`.
- Hybrid Analysis (Falcon Sandbox) — set `hybrid_analysis.api_key`.
- Hashlookup (CIRCL) — no key required; uses `/lookup/{hash_type}/{hash}`.
- MalwareBazaar auth key (optional) — set under `malwarebazaar.api_key` for privileged calls.

Use `samples/sample_config_extended.yaml` as a template, or `samples/sample_config_with_user_keys.yaml` prefilled.

## Hash Type Support per Source

Not every threat intel service accepts every hash type.  
This tool auto-detects MD5/SHA-1/SHA-256 and normalizes inputs.  
Where a source requires a specific type, the tool adapts automatically (e.g., converts to MD5 for MalShare).

| Vendor / Source   | MD5 | SHA-1 | SHA-256 | Notes                                                                 |
|-------------------|-----|-------|---------|-----------------------------------------------------------------------|
| **VirusTotal**    | ✔️   | ✔️     | ✔️       | Any hash type works; SHA-256 preferred.                               |
| **MalwareBazaar** | ✔️   | ✔️     | ✔️       | All accepted; SHA-256 most common.                                    |
| **URLHaus**       | ❌   | ❌     | ✔️       | Only SHA-256 supported for payload lookups.                           |
| **ThreatFox**     | ✔️   | ✔️     | ✔️       | Any hash type accepted.                                               |
| **OTX**           | ✔️   | ✔️     | ✔️       | Any hash type accepted.                                               |
| **Hybrid Analysis** | ✔️ | ✔️     | ✔️       | Any hash type accepted.                                               |
| **Hashlookup (CIRCL)** | ✔️ | ✔️ | ✔️       | Endpoint requires specifying type (`/lookup/md5/...`, `/sha1/...`).   |
| **MalShare**      | ✔️   | ❌     | ❌       | **MD5 only.** Tool resolves MD5 via VirusTotal when given SHA-1/256.  |

### Practical Notes
- **Always prefer SHA-256** when you have it — it is globally unique and supported everywhere except MalShare.  
- **MalShare**: requires MD5. The tool fetches MD5 from VirusTotal automatically.  
- **URLHaus**: requires SHA-256. If you only have MD5/SHA-1, results may be empty.  
- **Fallbacks**: If a source cannot handle the hash type, the tool either skips or converts where possible.
### Query Flow Overview

Below is how a single hash query flows through the tool:

User Input (hash or filename)
│
▼
Auto-detect type (MD5 / SHA-1 / SHA-256)
│
▼
Normalize (lowercase, strip, etc.)
│
▼
┌─────────────────────────────┐
│ Per-source adapters: │
│ │
│ - VirusTotal: MD5/SHA1/SHA256 (any)
│ - MalwareBazaar: MD5/SHA1/SHA256
│ - URLHaus: force SHA-256
│ - ThreatFox: MD5/SHA1/SHA256
│ - OTX: MD5/SHA1/SHA256
│ - Hybrid Analysis: MD5/SHA1/SHA256
│ - Hashlookup (CIRCL): use correct type in URL
│ - MalShare: force MD5 (resolve from VT if only SHA-256 given)
└─────────────────────────────┘
│
▼
Merge all source results
│
▼
Apply vendor allowlist (filter AV matches)
│
▼
Cache → Save to JSON (TTL configurable)
│
▼
Report (CSV / XLSX / GUI table)

pgsql
Copy code

**Key points:**
- You can paste **any hash type**; the tool adapts per source.
- Conversion logic ensures sources like **MalShare (MD5)** and **URLHaus (SHA-256)** are queried correctly.
- All results are cached per hash (using normalized SHA-256 as the key).