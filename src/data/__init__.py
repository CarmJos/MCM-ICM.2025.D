# ------------------ Helper Functions ------------------
from typing import Optional

import pandas as pd


def safe_int(value) -> Optional[int]:
    try:
        return int(float(value)) if pd.notna(value) else None
    except ValueError:
        return None


def safe_float(value) -> Optional[float]:
    try:
        return float(value) if pd.notna(value) else None
    except ValueError:
        return None
