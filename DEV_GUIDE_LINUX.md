# Koioscope — Linux Developer Handbook (Source → Build → Portable Bundle)

This guide explains how to develop, build, and package Koioscope on Linux. It is intended for developers, not end-users.

---

## 0) Supported targets & what you’ll build

- **Target OS**: Linux x86_64 (Ubuntu/Debian/Fedora/RHEL and similar).  
- **Python**: 3.10+  
- **Build output**:  
  - **Onedir** PyInstaller bundles (recommended)  
  - Packaged as `Koioscope-Linux-x64-portable.tar.gz`  
- **GUI**: Tkinter (needs `python3-tk` at build-time to run from source; not required for the built bundle)

> ⚠️ Cross-compiling is not supported. Build the Linux bundle **on Linux**.

---

## 1) Prepare a clean Linux dev environment

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip python3-tk build-essential git
```

### Fedora/RHEL/CentOS
```bash
sudo dnf install -y python3 python3-venv python3-pip python3-tkinter gcc gcc-c++ make git
```

---

## 2) Get the source

Git:
```bash
git clone <YOUR-REPO-URL> koioscope
cd koioscope
```

ZIP:
```bash
unzip Koioscope-source.zip -d koioscope
cd koioscope
```

Repo should contain:
```
koioscope/
samples/
tests/
README.md
requirements.txt
```

---

## 3) Create & activate venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5) Configuration

```bash
cp samples/sample_config_extended.yaml config.yaml
nano config.yaml
```

Fill in API keys, rate limits, vendor allowlist, proxy if needed.

---

## 6) Run from source

GUI:
```bash
python -m koioscope.gui --config config.yaml
```

CLI:
```bash
python -m koioscope.cli --config config.yaml --query <hash>
python -m koioscope.cli --config config.yaml --batch samples/sample_batch.csv --out out/report.csv
```

---

## 7) Run tests

```bash
pytest -q
```

---

## 8) Build Linux binaries

```bash
pip install pyinstaller

# GUI
python -m PyInstaller --windowed --name Koioscope-GUI -p . koioscope/gui.py

# CLI
python -m PyInstaller --name koioscope -p . koioscope/cli.py
```

Output:
```
dist/
  Koioscope-GUI/
  koioscope/
```

---

## 9) Stage a release folder

```bash
rm -rf release
mkdir -p release/Koioscope/cli

cp -r dist/Koioscope-GUI/* release/Koioscope/
cp -r dist/koioscope/*    release/Koioscope/cli/
cp README.md release/Koioscope/
cp -r samples release/Koioscope/samples
cp samples/sample_config_extended.yaml release/Koioscope/config.yaml
```

### Launchers

GUI:
```bash
cat > release/Koioscope/Koioscope-GUI.sh << 'SH'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/Koioscope-GUI" --config "$DIR/config.yaml"
SH
chmod +x release/Koioscope/Koioscope-GUI.sh
```

CLI:
```bash
cat > release/Koioscope/Koioscope-CLI.sh << 'SH'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/cli/koioscope" --config "$DIR/config.yaml" "$@"
SH
chmod +x release/Koioscope/Koioscope-CLI.sh
```

---

## 10) Package tarball

```bash
cd release
tar -czvf ../Koioscope-Linux-x64-portable.tar.gz Koioscope
cd ..
```

---

## 11) Test tarball

```bash
tar -xvzf Koioscope-Linux-x64-portable.tar.gz -C ~/tmp
cd ~/tmp/Koioscope
./Koioscope-GUI.sh
./Koioscope-CLI.sh --query 44d88612fea8a8f36de82e1278abb02f
```

---

## 12) Logs & cache

- Logs: `${XDG_STATE_HOME:-~/.local/state}/Koioscope/logs/run.jsonl`
- Cache: `~/.local/share/Koioscope/cache`

---

## 13) Troubleshooting

- Install `python3-tk` if Tkinter missing.
- Use **absolute imports** in `cli.py` and `gui.py`.
- Always ship entire onedir folder.
- Adjust API keys / rate limits if 401/403/429 errors.

---

## 14) Docker build (optional)

Dockerfile example:
```Dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip python3-tk build-essential git
WORKDIR /src
COPY . /src
RUN python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pip install pyinstaller  && python -m PyInstaller --windowed --name Koioscope-GUI -p . koioscope/gui.py  && python -m PyInstaller --name koioscope -p . koioscope/cli.py
```

---

## 15) Versioning & release

`koioscope/__init__.py`:
```python
__app_name__ = "Koioscope"
__version__  = "0.2.0"
```

Tag & release:
```bash
git tag v0.2.0
git push --tags
```

Artifacts:
- `Koioscope-Linux-x64-portable.tar.gz`
- `Koioscope-source.zip`

---
