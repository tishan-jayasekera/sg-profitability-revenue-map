from __future__ import annotations

import numpy as np
import pandas as pd

def top_loss_jobs(job_month_summary: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    df = job_month_summary.copy()
    df["gm"] = pd.to_numeric(df["gm"], errors="coerce").fillna(0.0)
    return df.sort_values("gm", ascending=True).head(n)

def overrun_tasks(job_task_summary: pd.DataFrame, min_quoted_hours: float = 1.0, n: int = 25) -> pd.DataFrame:
    df = job_task_summary.copy()
    df["quoted_hours"] = pd.to_numeric(df["quoted_hours"], errors="coerce").fillna(0.0)
    df = df[df["quoted_hours"] >= min_quoted_hours].copy()
    df["overrun_pct"] = np.where(df["quoted_hours"] != 0, df["hour_variance"] / df["quoted_hours"], np.nan)
    return df.sort_values("overrun_pct", ascending=False).head(n)

def unquoted_work(job_task_summary: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    df = job_task_summary.copy()
    df = df[df["is_unquoted_task"]].copy()
    return df.sort_values("actual_hours", ascending=False).head(n)
