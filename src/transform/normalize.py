from __future__ import annotations

import re
import pandas as pd

def clean_job_no(x) -> str:
    """Normalise job numbers coming from Excel (floats, trailing .0, spaces)."""
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = s.replace("\u00a0", " ")
    # Strip trailing .0 from Excel floats
    s = re.sub(r"\.0+$", "", s)
    # Keep alnum and common separators
    s = re.sub(r"[^0-9A-Za-z\-_/]", "", s)
    return s

def clean_task_name(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = re.sub(r"\s+", " ", s)
    return s

def month_key_first_of_month(dt: pd.Series | pd.Timestamp) -> pd.Series | pd.Timestamp:
    """Return a first-of-month timestamp (MonthKey) from a datetime series or scalar."""
    if isinstance(dt, pd.Timestamp):
        return pd.Timestamp(year=dt.year, month=dt.month, day=1)
    d = pd.to_datetime(dt, errors="coerce")
    return pd.to_datetime(dict(year=d.dt.year, month=d.dt.month, day=1), errors="coerce")
