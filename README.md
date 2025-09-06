# Koioscope — Hash & Filename Intel Lookup (GUI + CLI)

![Koioscope GUI](https://github.com/bijey-ang/Koioscope-Hash-Tool/blob/main/koioscope.jpeg)

Koioscope is a cross‑platform tool for analysts to check **hashes and filenames** against multiple **free OSINT/threat‑intel sources**. It includes both a **minimal GUI** (Tk/Tkinter) and a **CLI**.

It supports **single** and **batch** modes, merges results across sources, caches responses, respects rate limits, and exports **CSV/XLSX** reports with a fixed schema.

---

## ✨ Features

- **Inputs**
  - Mode A: Single query (hash or filename)
  - Mode B: Batch from CSV/XLSX (columns: `hash[, comment]`)
  - Auto‑detect & normalize **MD5 / SHA‑1 / SHA‑256**
- **Sources** (permanently‑free tiers; configure in `config.yaml`)
  - **VirusTotal** (public API JSON) + **permalink HTML parsing** (fills fields missing from API)
  - **abuse.ch**: URLHaus, MalwareBazaar (Auth Key), ThreatFox
  - **OTX (AlienVault)** free tier
  - **MalShare** (API key; **MD5‑only**)
  - **Hybrid Analysis** (API key)
  - **CIRCL Hashlookup**
- **Engineering**
  - Caching (per‑hash JSON), TTL, vendor allowlist filter
  - Structured logging (console + JSONL), retries/backoff/timeouts
  - Cross‑platform: Windows / Linux / macOS, Python ≥ 3.10
  - Unit tests (parsing, normalization, merging)
- **Reports (CSV/XLSX)**
  - fixed schema: see **Report Schema** below
  - includes source permalinks

---

## 📦 What’s in this repository

```
koioscope/               # Python package (source)
samples/                 # sample_config_extended.yaml, sample_batch.(csv|xlsx), vendor_allowlist.txt
tests/                   # pytest unit tests
docs/                    # USER_GUIDE.md, LINUX_USER_GUIDE.md, DEV_GUIDE(_LINUX|_MACOS).md
scripts/                 # optional build/staging scripts
README.md                # this file
requirements.txt         # runtime/dev deps
CHANGELOG.md             # (optional) version history
CONTRIBUTING.md          # (optional) how to contribute
SECURITY.md              # (optional) security contact/process
LICENSE                  # license for this repository
.gitignore               # ignores build artifacts, venv, logs, etc.
```

> 🔒 **Never commit API keys**. Keep `config.yaml` outside source control or as a template in `samples/`.

---

## 🚀 Quick Start for End‑Users (Portable Bundles)

Portable bundles are available in **GitHub Releases**. Download the one for your OS.

### Windows

1) **Unzip** `Koioscope-Windows-x64-portable.zip`  
2) Open the folder `Koioscope/` and **edit** `config.yaml` (add API keys).  
3) **Run GUI**: double‑click `Koioscope-GUI.bat`  
   **CLI**: run `Koioscope-CLI.bat --query <hash>`

**Logs**: `%LOCALAPPDATA%\Koioscope\logs\run.jsonl`  
**Cache**: `%LOCALAPPDATA%\Koioscope\cache`

---

### Linux

1) `tar -xvzf Koioscope-Linux-x64-portable.tar.gz`  
2) `cd Koioscope` and **edit** `config.yaml`  
3) **Run GUI**: `./Koioscope-GUI.sh` (first `chmod +x` if needed)  
   **CLI**: `./Koioscope-CLI.sh --query <hash>`

**Logs**: `${XDG_STATE_HOME:-~/.local/state}/Koioscope/logs/run.jsonl`  
**Cache**: `~/.local/share/Koioscope/cache`

---

### macOS

1) **Unzip** `Koioscope-macOS-<arch>-portable.zip` (`arm64` for Apple Silicon, `x86_64` for Intel)  
2) Open `Koioscope/` and **edit** `config.yaml`  
3) **Run GUI**: double‑click `Koioscope-GUI.command`  
   **CLI**: `./Koioscope-CLI.command --query <hash>`

If blocked by Gatekeeper, run inside the folder:
```bash
xattr -dr com.apple.quarantine .
chmod +x Koioscope-GUI.command Koioscope-CLI.command
```

**Logs**: `~/Library/Logs/Koioscope/run.jsonl`  
**Cache**: `~/Library/Application Support/Koioscope/cache`

For detailed end‑user steps per OS, see **docs/USER_GUIDE.md**, **docs/LINUX_USER_GUIDE.md**, and **docs/MACOS_USER_GUIDE.md**.

---

## 🛠️ Run from Source (Developers)

> Requires Python **3.10+**. Recommended: use a **virtual environment**.

### 1) Clone & venv

```bash
git clone https://github.com/<your-org-or-user>/Koioscope-Hash-Tool.git
cd Koioscope-Hash-Tool
python -m venv .venv        # Windows: python ; macOS/Linux: python3
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Configure

```bash
cp samples/sample_config_extended.yaml config.yaml
# edit config.yaml and add your API keys/rates/proxy/cache
```

### 3) Run

GUI:
```bash
python -m koioscope.gui --config config.yaml
```

CLI:
```bash
python -m koioscope.cli --config config.yaml --query 44d88612fea8a8f36de82e1278abb02f

# Batch CSV → CSV
python -m koioscope.cli --config config.yaml --batch samples/sample_batch.csv --out out/report.csv

# Batch XLSX → XLSX
python -m koioscope.cli --config config.yaml --batch samples/sample_batch.xlsx --out out/report.xlsx

# With vendor allowlist filter
python -m koioscope.cli --config config.yaml --batch samples/sample_batch.csv \
  --vendor-list samples/vendor_allowlist.txt --out out/report.csv
```

### 4) Test

```bash
pytest -q
```

> Linux only: install Tk if missing → `sudo apt-get install -y python3-tk`  
> macOS: prefer Python from **python.org** if Tk issues appear.

For detailed developer guides, see **docs/DEV_GUIDE.md**, **docs/DEV_GUIDE_LINUX.md**, **docs/DEV_GUIDE_MACOS.md**.

---

## 🧰 Build Portable Bundles (Developers)

We recommend **PyInstaller onedir** builds per OS (build **on** the target OS).

### Windows (PowerShell)

```powershell
# Clean
Remove-Item -Recurse -Force .\build,.\dist -ErrorAction SilentlyContinue

# Build GUI + CLI
python -m PyInstaller --windowed --icon ".\koioscope\resources\koioscope.ico" --name Koioscope-GUI -p . koioscope\gui.py
python -m PyInstaller           --icon ".\koioscope\resources\koioscope.ico" --name koioscope      -p . koioscope\cli.py

# Stage release
Remove-Item -Recurse -Force .\release -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path .\release\Koioscope,.\release\Koioscope\cli | Out-Null
Copy-Item .\dist\Koioscope-GUI\* .\release\Koioscope\ -Recurse -Force
Copy-Item .\dist\koioscope\*    .\release\Koioscope\cli\ -Recurse -Force
Copy-Item .\README.md           .\release\Koioscope\README.md -Force
Copy-Item .\samples\* -Recurse  .\release\Koioscope\samples\ -Force
Copy-Item .\samples\sample_config_extended.yaml .\release\Koioscope\config.yaml -Force

# Launchers
"@echo off`nstart "" ""%~dp0Koioscope-GUI.exe"" --config ""%~dp0config.yaml""" |
  Set-Content .\release\Koioscope\Koioscope-GUI.bat -Encoding ASCII
"@echo off`n""%~dp0cli\koioscope.exe"" --config ""%~dp0config.yaml"" %*" |
  Set-Content .\release\Koioscope\Koioscope-CLI.bat -Encoding ASCII

# Zip
Compress-Archive -Path .\release\Koioscope\* -DestinationPath Koioscope-Windows-x64-portable.zip
```

---

### Linux (Bash)

```bash
sudo apt-get update && sudo apt-get install -y python3-tk build-essential
pip install pyinstaller

# Clean
rm -rf build dist release

# Build GUI + CLI
python -m PyInstaller --windowed --name Koioscope-GUI -p . koioscope/gui.py
python -m PyInstaller           --name koioscope      -p . koioscope/cli.py

# Stage
mkdir -p release/Koioscope/cli
cp -r dist/Koioscope-GUI/* release/Koioscope/
cp -r dist/koioscope/*    release/Koioscope/cli/
cp README.md release/Koioscope/
mkdir -p release/Koioscope/samples && cp -r samples/* release/Koioscope/samples/
cp samples/sample_config_extended.yaml release/Koioscope/config.yaml

# Launchers
cat > release/Koioscope/Koioscope-GUI.sh << 'SH'
#!/bin/bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/Koioscope-GUI" --config "$DIR/config.yaml"
SH
chmod +x release/Koioscope/Koioscope-GUI.sh

cat > release/Koioscope/Koioscope-CLI.sh << 'SH'
#!/bin/bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/cli/koioscope" --config "$DIR/config.yaml" "$@"
SH
chmod +x release/Koioscope/Koioscope-CLI.sh

# Package
tar -czvf Koioscope-Linux-x64-portable.tar.gz -C release Koioscope
```

---

### macOS (zsh)

```bash
# Prereqs: xcode-select --install ; prefer python.org Python for Tk

pip install pyinstaller
rm -rf build dist release

# (Optional) convert PNG → ICNS for app icon
# ... see docs/DEV_GUIDE_MACOS.md section 5

# Build GUI + CLI
pyinstaller --windowed --name Koioscope-GUI -p . koioscope/gui.py
pyinstaller           --name koioscope      -p . koioscope/cli.py

# Stage
mkdir -p release/Koioscope/cli
cp -R dist/Koioscope-GUI.app release/Koioscope/
cp -R dist/koioscope/*        release/Koioscope/cli/
cp README.md release/Koioscope/
mkdir -p release/Koioscope/samples && cp -R samples/* release/Koioscope/samples/
cp samples/sample_config_extended.yaml release/Koioscope/config.yaml

# Launchers
cat > release/Koioscope/Koioscope-GUI.command << 'SH'
#!/bin/zsh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
open -a "$DIR/Koioscope-GUI.app" --args --config "$DIR/config.yaml"
SH
chmod +x release/Koioscope/Koioscope-GUI.command

cat > release/Koioscope/Koioscope-CLI.command << 'SH'
#!/bin/zsh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/cli/koioscope" --config "$DIR/config.yaml" "$@"
SH
chmod +x release/Koioscope/Koioscope-CLI.command

# Zip
cd release && zip -r ../Koioscope-macOS-$(uname -m)-portable.zip Koioscope && cd ..
```

> (Optional) macOS **codesign + notarize** for best UX — see `docs/DEV_GUIDE_MACOS.md` §9.

---

## ⚙️ Configuration (`config.yaml`)

Key sections:

```yaml
virustotal:
  enabled: true
  api_key: "<YOUR_VT_PUBLIC_KEY>"
  rate_limit: { requests_per_minute: 4 }

malwarebazaar:
  enabled: true
  api_key: "<YOUR_MALWAREBAZAAR_AUTH_KEY>"
  rate_limit: { requests_per_minute: 10 }

malshare:
  enabled: true
  api_key: "<YOUR_MALSHARE_API_KEY>"
  rate_limit: { requests_per_minute: 10 }   # MD5-only

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

cache:
  dir: "<user-writable path per OS>"
  ttl_minutes: 1440

# Optional proxy
# http_proxy:  "http://user:pass@proxy.company.com:8080"
# https_proxy: "http://user:pass@proxy.company.com:8080"

# Optional vendor allowlist is given as a file (see CLI/GUI)
```

**Notes**
- **MalShare**: requires **MD5**; Koioscope autodiscovers MD5 via VT when possible.
- **URLHaus**: primarily uses SHA‑256.
- Obey each source’s **TOS** and **rate limits**. Public VT keys are typically ~4 rpm.

---

## 📄 Report Schema (CSV/XLSX)

Columns written in this order:

```
hash,
comment,
av_vendor_matches,         # filtered by your vendor allowlist (if provided)
filenames,                 # names seen in the wild
pe_description,
pe_original_filename,
pe_copyright,
signer,                    # if available (PE signature)
vt_detection_ratio,        # e.g., 12/70
first_seen,                # earliest first-seen across sources
last_seen,                 # latest last-seen across sources
indicator_tags,            # e.g., Harmless, Signed, Expired, Revoked, MSSoftware
source_links               # VT permalink + others
```

---

## 🐛 Troubleshooting (common)

- **401/403** → Missing/invalid API key in `config.yaml`  
- **429** → Rate limit exceeded → lower `requests_per_minute`  
- **Proxy** → Set `http_proxy` / `https_proxy` in config or env vars  
- **PyInstaller build IMPORT errors** → Use **absolute imports** in `gui.py` / `cli.py`  
- **GUI won’t open portable on macOS** → see **Gatekeeper** steps above  
- **“Permission denied” on Linux/macOS launchers** → `chmod +x` the `.sh`/`.command` files  
- **Reports fail to write** → write to a user‑writable folder and proper extension (`.csv` / `.xlsx`)  
- **Batch errors** → CSV header is `hash, comment`; XLSX first sheet must match those column names

---

## 🔐 Security & Privacy

- Do not submit confidential or sensitive samples to OSINT services without approval.  
- Understand and comply with VirusTotal and each vendor’s **Terms of Service**.  
- Avoid committing `config.yaml` with real API keys.

---

## 🧾 License

See `LICENSE`.  
> If this repository uses a **restrictive** license, forks/modifications may be prohibited. If it uses an **open‑source** license (e.g., Apache‑2.0/MIT), follow the terms therein.

---

## 🤝 Contributing

1. Fork & clone
2. Create a branch
3. Add tests for any changes (`pytest -q`)
4. Open a Pull Request

See `CONTRIBUTING.md` for style and review guidelines.

---

## 🗺️ Roadmap / Ideas

- Optional YARA matches (where permitted)
- Pluggable source framework
- Parallel query orchestration
- More file type metadata parsers

---

## 🏷 Versioning & Releases

- Set version in `koioscope/__init__.py`:
  ```python
  __app_name__ = "Koioscope"
  __version__  = "0.2.0"
  ```
- Tag & release:
  ```bash
  git tag v0.2.0
  git push --tags
  ```
- Upload portable bundles under **GitHub Releases** with checksums.

---

## 🙌 Credits

Built by security engineers for security engineers. Thanks to VirusTotal, abuse.ch (URLHaus / MalwareBazaar / ThreatFox), AlienVault OTX, MalShare, Hybrid Analysis, and CIRCL Hashlookup for their community APIs.
