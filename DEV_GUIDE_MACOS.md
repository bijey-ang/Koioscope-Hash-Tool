# Koioscope — macOS Developer Handbook (Source → Build → Portable Bundle)

This guide explains how to **develop, build, and package Koioscope on macOS**. It is for developers (not end‑users). The result is a portable ZIP you can ship to users.

> PyInstaller does **not** cross‑compile across CPU architectures. Build on the same arch you’ll distribute for:
> - Apple Silicon → `arm64` (M1/M2/M3…)
> - Intel Mac → `x86_64`
> You can build **both** by running the steps once on each type of Mac.

---

## 0) What you’ll build

- **GUI**: `Koioscope-GUI.app` (PyInstaller onedir bundle)
- **CLI**: onedir folder containing the `koioscope` executable
- **Portable ZIP**: `Koioscope-macOS-<arch>-portable.zip` (includes `.app`, CLI, samples, config, launchers)

---

## 1) Prerequisites

### 1.1 Xcode Command Line Tools
```bash
xcode-select --install
```

### 1.2 Python 3.10+ (choose ONE)

**Option A — python.org (recommended for hassle‑free Tk)**  
Download “macOS 64‑bit universal2 installer” from https://www.python.org/downloads/ and run it.  
Check:
```bash
python3 --version
pip3 --version
```

**Option B — Homebrew**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11 tcl-tk
# Apple Silicon default Homebrew prefix is /opt/homebrew; Intel is /usr/local
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zprofile  # adjust for Intel if needed
echo 'export TK_SILENCE_DEPRECATION=1' >> ~/.zprofile
exec zsh -l
python3 --version
```

> If Tk errors occur with Homebrew Python, prefer the **python.org** build.

---

## 2) Get the source & create a virtual environment

```bash
# Clone (or unzip)
git clone https://github.com/<your-user-or-org>/Koioscope-Hash-Tool.git koioscope
cd koioscope

# Create & activate venv
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip & install deps
python -m pip install --upgrade pip wheel
pip install -r requirements.txt
```

---

## 3) Configure Koioscope for development

```bash
cp samples/sample_config_extended.yaml config.yaml
open -e config.yaml   # or: nano config.yaml
```
Edit API keys and settings (VT, MalwareBazaar, MalShare, Hybrid Analysis, OTX optional), set rate limits, proxy if needed.  
Recommended user paths on macOS:
```yaml
cache:
  dir: "~/Library/Application Support/Koioscope/cache"
  ttl_minutes: 1440
```

---

## 4) Run from source (sanity check)

GUI:
```bash
python -m koioscope.gui --config config.yaml
```

CLI:
```bash
python -m koioscope.cli --config config.yaml --query 44d88612fea8a8f36de82e1278abb02f
python -m koioscope.cli --config config.yaml --batch samples/sample_batch.csv --out out/report.csv
```

Tests:
```bash
pytest -q
```

> If Tk crashes or is missing, confirm you’re using python.org Python; or `brew install tcl-tk` and relaunch your shell.

---

## 5) Prepare an app icon (.icns)

If you have a PNG (e.g., `koioscope/resources/koioscope.png`), generate `.icns`:

```bash
mkdir -p build/icons.iconset
sips -z 16 16     koioscope/resources/koioscope.png --out build/icons.iconset/icon_16x16.png
sips -z 32 32     koioscope/resources/koioscope.png --out build/icons.iconset/icon_16x16@2x.png
sips -z 32 32     koioscope/resources/koioscope.png --out build/icons.iconset/icon_32x32.png
sips -z 64 64     koioscope/resources/koioscope.png --out build/icons.iconset/icon_32x32@2x.png
sips -z 128 128   koioscope/resources/koioscope.png --out build/icons.iconset/icon_128x128.png
sips -z 256 256   koioscope/resources/koioscope.png --out build/icons.iconset/icon_128x128@2x.png
sips -z 256 256   koioscope/resources/koioscope.png --out build/icons.iconset/icon_256x256.png
sips -z 512 512   koioscope/resources/koioscope.png --out build/icons.iconset/icon_256x256@2x.png
sips -z 512 512   koioscope/resources/koioscope.png --out build/icons.iconset/icon_512x512.png
cp koioscope/resources/koioscope.png build/icons.iconset/icon_512x512@2x.png
iconutil -c icns build/icons.iconset -o build/koioscope.icns
```

---

## 6) Build onedir bundles with PyInstaller

```bash
pip install pyinstaller
rm -rf build dist

# GUI .app
pyinstaller --windowed \
  --name Koioscope-GUI \
  --icon build/koioscope.icns \
  -p . \
  koioscope/gui.py

# CLI
pyinstaller \
  --name koioscope \
  -p . \
  koioscope/cli.py
```

Result:
```
dist/
  Koioscope-GUI.app/
  koioscope/
    koioscope        # CLI executable (Mach-O)
    _internal/...
```

> Ensure **absolute imports** in `koioscope/gui.py` and `koioscope/cli.py` (e.g., `from koioscope.config import ...`). Relative imports cause PyInstaller runtime errors.

---

## 7) Stage a portable folder

```bash
rm -rf release
mkdir -p release/Koioscope/cli
cp -R dist/Koioscope-GUI.app release/Koioscope/
cp -R dist/koioscope/*        release/Koioscope/cli/

# Docs + samples + default config
cp README.md release/Koioscope/
mkdir -p release/Koioscope/samples
cp -R samples/* release/Koioscope/samples/
cp samples/sample_config_extended.yaml release/Koioscope/config.yaml
```

### Add double‑clickable launchers (.command)

**GUI launcher**:
```bash
cat > release/Koioscope/Koioscope-GUI.command << 'SH'
#!/bin/zsh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
open -a "$DIR/Koioscope-GUI.app" --args --config "$DIR/config.yaml"
SH
chmod +x release/Koioscope/Koioscope-GUI.command
```

**CLI launcher**:
```bash
cat > release/Koioscope/Koioscope-CLI.command << 'SH'
#!/bin/zsh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/cli/koioscope" --config "$DIR/config.yaml" "$@"
SH
chmod +x release/Koioscope/Koioscope-CLI.command
```

Folder now:
```
release/Koioscope/
  Koioscope-GUI.app
  Koioscope-GUI.command
  cli/koioscope
  Koioscope-CLI.command
  config.yaml
  README.md
  samples/
```

---

## 8) Zip the portable bundle

```bash
cd release
zip -r ../Koioscope-macOS-$(uname -m)-portable.zip Koioscope
cd ..
```
Example output: `Koioscope-macOS-arm64-portable.zip` (on Apple Silicon).

---

## 9) (Optional) Codesign & Notarize for best UX

Unsigned apps trigger Gatekeeper warnings. For internal use you can instruct users to remove quarantine (see §10). For general distribution, **codesign + notarize** is recommended.

### 9.1 Codesign
- Requires Apple Developer ID Application certificate in your Keychain.
```bash
codesign --force --deep --options runtime \
  --sign "Developer ID Application: <Your Name or Org>" \
  release/Koioscope/Koioscope-GUI.app

codesign --force \
  --sign "Developer ID Application: <Your Name or Org>" \
  release/Koioscope/cli/koioscope

codesign --verify --deep --strict --verbose=2 release/Koioscope/Koioscope-GUI.app
```

### 9.2 Notarize
```bash
# Zip .app for notarization
ditto -c -k --keepParent release/Koioscope/Koioscope-GUI.app Koioscope-GUI-notary.zip

# Submit (requires Apple ID, Team ID, and app-specific password)
xcrun notarytool submit Koioscope-GUI-notary.zip \
  --apple-id "<APPLE_ID_EMAIL>" \
  --team-id "<TEAMID>" \
  --password "<APP_SPECIFIC_PASSWORD>" \
  --wait

# Staple
xcrun stapler staple release/Koioscope/Koioscope-GUI.app
```

Re‑zip your final portable bundle afterward.

---

## 10) Sanity test like an end‑user

```bash
cd release
unzip Koioscope-macOS-$(uname -m)-portable.zip -d ~/tmp
cd ~/tmp/Koioscope

# If unsigned/quarantined:
xattr -dr com.apple.quarantine .

# Launch
open Koioscope-GUI.command
./Koioscope-CLI.command --query 44d88612fea8a8f36de82e1278abb02f
```

Logs default to: `~/Library/Logs/Koioscope/run.jsonl` (or as configured).  
Cache default: `~/Library/Application Support/Koioscope/cache` (if set in config).

---

## 11) Troubleshooting

- **Tk errors**: Prefer python.org Python; if using Brew, ensure `brew install tcl-tk` and `TK_SILENCE_DEPRECATION=1` is set. Restart shell.
- **Relative import errors in packaged app**: switch to **absolute imports** in `gui.py`/`cli.py`.
- **Gatekeeper blocks app**: either codesign+notarize (§9) or instruct users to run `xattr -dr com.apple.quarantine <Koioscope folder>`.
- **Permissions writing outputs**: choose a user‑writable folder (e.g., `~/Documents/Koioscope/out`).
- **Network 401/403/429**: fix API keys, lower rate limits, or configure `http_proxy`/`https_proxy` in `config.yaml`.

---

## 12) Developer checklist (macOS)

- [ ] Xcode CLT installed
- [ ] Python 3.10+ (python.org preferred)
- [ ] `python -m venv .venv` and `pip install -r requirements.txt`
- [ ] `config.yaml` with valid API keys
- [ ] `pytest -q` passes; GUI/CLI run from source
- [ ] PyInstaller onedir: `.app` + CLI bundle produced
- [ ] `release/Koioscope` staged with launchers, samples, config
- [ ] `Koioscope-macOS-<arch>-portable.zip` created
- [ ] (Optional) codesigned and notarized
- [ ] Sanity tested on a clean user account

---
