from __future__ import annotations

import io
from typing import Dict
import pandas as pd

def to_excel_bytes(tables: Dict[str, pd.DataFrame]) -> bytes:
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in tables.items():
            safe = name[:31].replace("/", "_")
            df.to_excel(writer, sheet_name=safe, index=False)
    return bio.getvalue()
