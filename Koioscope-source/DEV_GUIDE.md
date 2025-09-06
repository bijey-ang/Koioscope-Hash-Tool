# Koioscope — Developer / GitHub Handbook (Source Package ZIP)

This guide is for developers who will run from **source**, modify code, or build releases.

---

## 1) Prerequisites

- Python 3.10+
- Windows/macOS/Linux
- Git
- Internet access
- Tk runtime (Linux/macOS if needed)

---

## 2) Get the source

```bash
git clone <repo-url> koioscope
cd koioscope
```

or unzip `Koioscope-source.zip`.

---

## 3) Create & activate venv

Windows:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4) Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5) Configuration

Copy template:

```bash
cp samples/sample_config_extended.yaml config.yaml
```

Edit API keys, rate limits, vendor list, proxy.

---

## 6) Run from source

GUI:

```bash
python -m koioscope.gui --config config.yaml
```

CLI:

```bash
python -m koioscope.cli --config config.yaml --query <hash>
```

---

## 7) Layout

```
koioscope/
  cli.py
  gui.py
  logging_setup.py
  ...
samples/
tests/
```

---

## 8) Testing

```bash
pytest -q
```

---

## 9) Building binaries

```powershell
python -m PyInstaller --windowed --icon ".\koioscope\resources\koioscope.ico" --name Koioscope-GUI -p . koioscope\gui.py
python -m PyInstaller           --icon ".\koioscope\resources\koioscope.ico" --name koioscope      -p . koioscope\cli.py
```

Stage into `release\Koioscope\` and zip.

---

## 10) Repo hygiene

Use `.gitignore` to skip venv, build, dist, cache, logs, etc.

---

## 11) Versioning

Set in `koioscope/__init__.py`:

```python
__app_name__ = "Koioscope"
__version__  = "0.2.0"
```

Tag in git, push, create GitHub release.
