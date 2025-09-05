from __future__ import annotations
import json, logging, os, sys
from datetime import datetime
from typing import Any

class JsonlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "msg": record.getMessage(),
            "name": record.name,
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def setup_logging(run_dir: str = "logs") -> logging.Logger:
    os.makedirs(run_dir, exist_ok=True)
    logger = logging.getLogger("hash_intel_lookup")
    logger.setLevel(logging.INFO)

    # Console (human)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(ch)

    # JSONL
    fh = logging.FileHandler(os.path.join(run_dir, "run.jsonl"), encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(JsonlFormatter())
    logger.addHandler(fh)
    return logger
