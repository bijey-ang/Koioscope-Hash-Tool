# Koioscope — Linux End‑User Handbook (Portable tar.gz)

This guide is for **non‑developers on Linux** using the **portable Koioscope bundle**. No root, no Python install, and no package manager required.

---

## 1) System requirements

- **OS:** Linux x86_64 (Ubuntu/Debian/Fedora/RHEL and similar)
- **Desktop:** Any X11/Wayland desktop (for GUI). On servers/headless, use the **CLI**.
- **Network:** Outbound access to:
  - `www.virustotal.com`, `otx.alienvault.com`, `urlhaus.abuse.ch`, `bazaar.abuse.ch`, `threatfox.abuse.ch`
  - `malshare.com`, `www.hybrid-analysis.com`, `hashlookup.circl.lu`
  - Your HTTP(S) proxy, if applicable
- **Disk space:** ~300–500 MB for the unpacked folder (includes runtime), extra for cache and reports.

> No admin rights required. All files run from your home directory.

---

## 2) What you received

A file named like: **`Koioscope-Linux-x64-portable.tar.gz`**

After extraction you will have a folder **`Koioscope/`** containing at least:

```
Koioscope/
  Koioscope-GUI           # GUI executable (ELF)
  Koioscope-GUI.sh        # GUI launcher (passes config automatically)
  cli/koioscope           # CLI executable
  Koioscope-CLI.sh        # CLI launcher
  config.yaml             # your editable settings
  README.md
  samples/                # sample CSV/XLSX, vendor list, sample config
  _internal/ …            # runtime files (do not delete/move)
```

> **Do not** move individual files out of this folder. Keep everything together.

---

## 3) Extract the tar.gz

Open a terminal in the folder where the tarball is located and run:

```bash
tar -xvzf Koioscope-Linux-x64-portable.tar.gz
cd Koioscope
```

If your file manager extracted it for you, just **open the `Koioscope` folder in a terminal** (`Right‑click → Open in Terminal`).

---

## 4) First‑time setup — edit `config.yaml`

1) Open `Koioscope/config.yaml` in a text editor (e.g., `gedit`, `nano`, or your preferred editor).  
2) Fill in your API keys and settings. Example:

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

# Cache (user-writable; recommended default)
cache: { dir: "~/.local/share/Koioscope/cache", ttl_minutes: 1440 }

# Optional enterprise proxy
# http_proxy:  "http://user:pass@proxy.company.com:8080"
# https_proxy: "http://user:pass@proxy.company.com:8080"
```

3) Save the file.

> You can restrict AV vendors shown in the report via an **allowlist** (one vendor per line). See `samples/vendor_allowlist.txt` and set it in the GUI/CLI when exporting.

---

## 5) Run the GUI (recommended for ad‑hoc checks)

From inside the **Koioscope** folder:

```bash
./Koioscope-GUI.sh
```

If you get “**Permission denied**”, make the launcher executable:
```bash
chmod +x Koioscope-GUI.sh
./Koioscope-GUI.sh
```

### Using the GUI
- **Single lookup:** enter a hash (MD5/SHA1/SHA256) or filename → optional comment → **Run Single**.
- **Batch lookup:** click **Run Batch** → choose a CSV/XLSX file.
  - CSV columns: `hash, comment` (comment optional)
  - XLSX: same column names in the first sheet
- **Export:** **Export CSV** or **Export XLSX** to your chosen location. The schema is fixed:
  ```
  hash, comment, av_vendor_matches, filenames,
  pe_description, pe_original_filename, pe_copyright,
  signer, vt_detection_ratio, first_seen, last_seen,
  indicator_tags, source_links
  ```
- **Open Permalink:** select a row and click **Open Permalink** to open the VT page.
- **Status & errors:** shown at the bottom of the window.

---

## 6) Run the CLI (for scripts/servers)

Open a terminal **in the Koioscope folder** and use the launcher:

```bash
# Single hash → console output + saved report (if --out is given)
./Koioscope-CLI.sh --query 44d88612fea8a8f36de82e1278abb02f

# Batch from CSV → CSV report
./Koioscope-CLI.sh --batch samples/sample_batch.csv --out out/batch_report.csv

# Batch from XLSX → XLSX report
./Koioscope-CLI.sh --batch samples/sample_batch.xlsx --out out/batch_report.xlsx

# With a vendor allowlist
./Koioscope-CLI.sh --batch samples/sample_batch.csv \
  --vendor-list samples/vendor_allowlist.txt \
  --out out/report.csv
```

> If you choose to run the binaries directly (not via `.sh`), pass `--config "$(pwd)/config.yaml"` yourself.

---

## 7) Hash behavior & sources (quick notes)

- Hash types (MD5/SHA1/SHA256) are auto‑detected and normalized.
- **MalShare** requires **MD5**; Koioscope resolves MD5 via VirusTotal when only SHA‑256 is known.
- **URLHaus** uses **SHA‑256** primarily.
- Other sources accept MD5/SHA1/SHA256.
- Results are **cached** locally and reused according to `ttl_minutes`.

---

## 8) Where files go

- **Logs:** `${XDG_STATE_HOME:-~/.local/state}/Koioscope/logs/run.jsonl`  
  View last lines:
  ```bash
  tail -n 50 ~/.local/state/Koioscope/logs/run.jsonl
  ```

- **Cache:** `~/.local/share/Koioscope/cache` (or as set in `config.yaml`)

- **Reports:** wherever you export them (e.g., your `Documents` folder).

> You can safely delete the cache to force fresh queries.

---

## 9) Troubleshooting

- **Nothing happens when I double‑click**  
  Some file managers don’t run `.sh` by double‑click. Open a terminal and run:
  ```bash
  ./Koioscope-GUI.sh
  ```

- **“Permission denied” when launching**  
  Make launchers executable:
  ```bash
  chmod +x Koioscope-GUI.sh Koioscope-CLI.sh
  ```

- **“Text file busy” or won’t run from Downloads**  
  Move the folder into your home (e.g., `~/Apps/Koioscope`). Avoid executing from noexec mounts.

- **Cannot open display / on a server**  
  Use the CLI launcher:
  ```bash
  ./Koioscope-CLI.sh --batch samples/sample_batch.csv --out out.csv
  ```

- **401/403 from a source**  
  Invalid/missing API key. Fix `config.yaml` (check for extra spaces or quotes).

- **429 / rate limit exceeded**  
  Lower the per‑source `requests_per_minute` in `config.yaml`, or try later.

- **Proxy required**  
  Set `http_proxy` / `https_proxy` in `config.yaml` (or export environment vars before launching).

- **Reports fail to save**  
  Choose a **writable** folder (e.g., `~/Documents`) and ensure the filename ends with `.csv` or `.xlsx`.

- **“File not found” for samples**  
  Keep the folder structure intact. Don’t move executables out of `Koioscope/`.

---

## 10) Updating Koioscope

1) Close Koioscope.  
2) Delete the **old `Koioscope/` folder**.  
3) Extract the **new** `Koioscope-Linux-x64-portable.tar.gz`.  
4) Copy your previous `config.yaml` into the new folder (overwrite).

---

## 11) Getting support

Include in your message:
- The last 50 lines of the log:  
  `tail -n 50 ~/.local/state/Koioscope/logs/run.jsonl`
- Your `config.yaml` **with API keys redacted**
- The exact command you ran (or what you clicked) and the file you tested

---

## 12) Quick reference (commands)

```bash
# Extract bundle
tar -xvzf Koioscope-Linux-x64-portable.tar.gz
cd Koioscope

# Launch GUI
chmod +x Koioscope-GUI.sh
./Koioscope-GUI.sh

# Launch CLI
chmod +x Koioscope-CLI.sh
./Koioscope-CLI.sh --query 44d88612fea8a8f36de82e1278abb02f

# View logs
tail -n 50 ~/.local/state/Koioscope/logs/run.jsonl
```
