# Koioscope — End-User Handbook (Portable ZIP)

This guide is for **non-developer users** who receive a **portable ZIP** of Koioscope for Windows. No admin rights or Python required.

---

## 1) System requirements

- Windows 10/11 (64-bit)
- Network access to: VirusTotal, OTX, urlhaus.abuse.ch, malwarebazaar.abuse.ch, threatfox.abuse.ch, MalShare, Hybrid Analysis, hashlookup.circl.lu
- Able to reach those domains through your proxy (if any)

---

## 2) What you received

A ZIP file like: `Koioscope-Windows-x64-portable.zip`

Inside, after unzipping, the folder **Koioscope** contains at least:

```
Koioscope\
  Koioscope-GUI.exe
  Koioscope-GUI.bat
  cli\koioscope.exe
  Koioscope-CLI.bat
  config.yaml
  README.md
  samples\
  _internal\ ...
```

---

## 3) First-time setup (edit `config.yaml`)

1. Open the **Koioscope** folder.
2. Right-click **`config.yaml` → Open with → Notepad**.
3. Fill in API keys, rate limits, vendor allowlist, proxy if needed.
4. Save and close Notepad.

---

## 4) Run the GUI (recommended)

- **Double-click** `Koioscope-GUI.bat`

### GUI usage
- Single lookup
- Batch lookup (CSV/XLSX)
- Export CSV/XLSX
- Open permalinks
- Status/errors shown at bottom

---

## 5) Run the CLI

Examples:

```powershell
.\Koioscope-CLI.bat --query 44d88612fea8a8f36de82e1278abb02f
.\Koioscope-CLI.bat --batch samples\sample_batch.csv --out out\batch_report.csv
```

---

## 6) Hash & source behavior

- MD5/SHA1/SHA256 auto-detected
- MalShare requires MD5; Koioscope resolves if missing
- Results cached in `%LOCALAPPDATA%\Koioscope\cache`

---

## 7) Logs & troubleshooting

- Logs: `%LOCALAPPDATA%\Koioscope\logs\run.jsonl`  
- Common errors: invalid API key, rate limit, proxy issues

---

## 8) Updating Koioscope

Delete old folder, unzip new ZIP, copy over `config.yaml`.

---

## 9) Getting help

Send last lines of `run.jsonl`, your `config.yaml` (with keys redacted), and exact command you ran.
