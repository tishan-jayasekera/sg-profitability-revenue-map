from __future__ import annotations

import io
from typing import Dict, Optional, Tuple
import pandas as pd

SHEET_ALIASES = {
    "timesheet": ["wfm", "timesheet", "time", "wfm hist", "wfm data"],
    "revrec": ["rev rec", "revrec", "revenue", "rev", "revenue recognition"],
    "quotes": ["quotes", "estimates", "estimate", "quote", "quotation"],
}

def _pick_sheet(sheets, aliases):
    sheets_l = {s.lower().strip(): s for s in sheets}
    for a in aliases:
        for k, v in sheets_l.items():
            if a in k:
                return v
    return None

def load_workbook(file_bytes: bytes) -> Dict[str, pd.DataFrame]:
    """Load an Excel workbook from uploaded bytes."""
    bio = io.BytesIO(file_bytes)
    xl = pd.ExcelFile(bio)
    sheets = xl.sheet_names

    ts_sheet = _pick_sheet(sheets, SHEET_ALIASES["timesheet"])
    rr_sheet = _pick_sheet(sheets, SHEET_ALIASES["revrec"])
    q_sheet  = _pick_sheet(sheets, SHEET_ALIASES["quotes"])

    out: Dict[str, pd.DataFrame] = {}
    if ts_sheet:
        out["timesheet"] = pd.read_excel(xl, ts_sheet)
    if rr_sheet:
        out["revrec"] = pd.read_excel(xl, rr_sheet)
    if q_sheet:
        out["quotes"] = pd.read_excel(xl, q_sheet)

    out["_meta"] = pd.DataFrame({
        "detected_sheets": [", ".join([f"timesheet={ts_sheet}", f"revrec={rr_sheet}", f"quotes={q_sheet}"])],
        "all_sheets": [", ".join(sheets)],
    })
    return out
