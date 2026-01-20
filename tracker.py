
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys
from filelock import FileLock

# ==========================
# EXE-SAFE BASE DIRECTORY
# ==========================
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

TRACE_LOG = BASE_DIR / "srv" / "data" / "trace_log.csv"
TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)

LOCK_FILE = TRACE_LOG.with_suffix(".lock")

# ==========================
# CONSTANTS
# ==========================
SOURCE_LOCATION = "Office"

# ==========================
# LOG MOVEMENT
# ==========================
def log_movement(
    item_id: str,
    location: str,
    status: str,
    model: str,
    substance: str,
):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with FileLock(str(LOCK_FILE)):

        if TRACE_LOG.exists():
            df = pd.read_csv(TRACE_LOG)
        else:
            df = pd.DataFrame(
                columns=[
                    "timestamp",
                    "item_id",
                    "location",
                    "status",
                    "model",
                    "substance",
                ]
            )

        # ==================================================
        # OFFICE-BASED INHERITANCE RULE
        # ==================================================
        if location != SOURCE_LOCATION and not df.empty:
            office_rows = df[
                (df["item_id"] == item_id) &
                (df["location"] == SOURCE_LOCATION)
            ]

            if not office_rows.empty:
                latest_office = (
                    office_rows
                    .sort_values("timestamp")
                    .iloc[-1]
                )
                model = latest_office["model"]
                substance = latest_office["substance"]
            else:
                model = "-"
                substance = "-"

        # ==================================================
        # WRITE ROW
        # ==================================================
        row = {
            "timestamp": timestamp,
            "item_id": item_id,
            "location": location,
            "status": status,
            "model": model,
            "substance": substance,
        }

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(TRACE_LOG, index=False)

    return row
