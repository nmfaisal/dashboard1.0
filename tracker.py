from pathlib import Path
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

TRACE_LOG = BASE_DIR / "srv" / "data" / "trace_log.csv"

# 🔴 THIS MUST RUN BEFORE to_csv
TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)

def log_movement(item_id: str, location: str, status: str, model: str, substance: str):
    timestamp = datetime.now().isoformat(timespec="seconds")

    row = {
        "timestamp": timestamp,
        "item_id": item_id,
        "location": location,
        "status": status,
        "model": model,
        "substance": substance,
    }

    if TRACE_LOG.exists():
        df = pd.read_csv(TRACE_LOG)
    else:
        df = pd.DataFrame(columns=row.keys())

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(TRACE_LOG, index=False)

    return row
