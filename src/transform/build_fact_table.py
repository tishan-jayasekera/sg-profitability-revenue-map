from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.config import ColumnMap
from src.transform.normalize import clean_job_no, clean_task_name, month_key_first_of_month

@dataclass
class FactOutputs:
    fact_job_task_month: pd.DataFrame
    job_month_summary: pd.DataFrame
    job_task_summary: pd.DataFrame
    qa: Dict[str, pd.DataFrame]

def build_fact_tables(timesheet: pd.DataFrame,
                      revrec: Optional[pd.DataFrame],
                      quotes: Optional[pd.DataFrame],
                      cols: ColumnMap = ColumnMap(),
                      revenue_allocation: str = "hours"  # hours | cost
                      ) -> FactOutputs:
    """
    Canonical pipeline (goal = your notebook):

    1) Normalise keys (job_no, task_name), derive MonthKey (first of month).
    2) Aggregate daily WFM → job_task_month (hours, cost, implied billable).
    3) Aggregate Rev Rec → job_month revenue.
    4) Allocate job_month revenue to job_task_month (by hours or cost share).
    5) Join quotes (job-level or job-task level) and compute variances.
    """

    ts = timesheet.copy()
    def _series_or_default(frame: pd.DataFrame, column: str, default: float) -> pd.Series:
        if column in frame.columns:
            return frame[column]
        return pd.Series(default, index=frame.index)

    # --- keys ---
    ts["job_no"] = ts[cols.ts_job_no].map(clean_job_no)
    ts["task_name"] = ts[cols.ts_task].map(clean_task_name)

    # --- dates ---
    ts["_time_date"] = pd.to_datetime(ts[cols.ts_date], errors="coerce")
    if cols.ts_month_key in ts.columns:
        ts["_month_key"] = pd.to_datetime(ts[cols.ts_month_key], errors="coerce")
        ts.loc[ts["_month_key"].isna(), "_month_key"] = month_key_first_of_month(ts.loc[ts["_month_key"].isna(), "_time_date"])
    else:
        ts["_month_key"] = month_key_first_of_month(ts["_time_date"])

    # --- measures ---
    # hours
    ts["hours"] = pd.to_numeric(_series_or_default(ts, cols.ts_hours, 0.0), errors="coerce").fillna(0.0)

    # rates
    ts["bill_rate"] = pd.to_numeric(_series_or_default(ts, cols.ts_bill_rate, np.nan), errors="coerce")
    ts["base_rate"] = pd.to_numeric(_series_or_default(ts, cols.ts_base_rate, np.nan), errors="coerce")
    ts["quoted_rate"] = pd.to_numeric(_series_or_default(ts, cols.ts_quoted_rate, np.nan), errors="coerce")

    # cost / implied revenue
    ts["cost"] = ts["hours"] * ts["base_rate"].fillna(0.0)
    ts["implied_billable"] = ts["hours"] * ts["bill_rate"].fillna(0.0)

    # --- aggregate to job_task_month ---
    gcols = ["job_no", "task_name", "_month_key"]
    agg = ts.groupby(gcols, dropna=False).agg(
        total_hours=("hours", "sum"),
        total_cost=("cost", "sum"),
        implied_billable=("implied_billable", "sum"),
        avg_bill_rate=("bill_rate", "mean"),
        avg_base_rate=("base_rate", "mean"),
    ).reset_index().rename(columns={"_month_key": "month_key"})

    # --- rev rec job_month ---
    if revrec is not None and len(revrec) > 0:
        rr = revrec.copy()
        rr["job_no"] = rr[cols.rr_job_no].map(clean_job_no)
        rr["month_key"] = month_key_first_of_month(pd.to_datetime(rr[cols.rr_month_key], errors="coerce"))
        rr["rev_rec_amount"] = pd.to_numeric(rr[cols.rr_amount], errors="coerce").fillna(0.0)
        rr_job_month = rr.groupby(["job_no", "month_key"], dropna=False).agg(
            job_month_rev=("rev_rec_amount", "sum")
        ).reset_index()
    else:
        rr_job_month = pd.DataFrame(columns=["job_no", "month_key", "job_month_rev"])

    # --- allocate revenue down to tasks ---
    fact = agg.merge(rr_job_month, on=["job_no", "month_key"], how="left")
    fact["job_month_rev"] = fact["job_month_rev"].fillna(0.0)

    # allocation weights (within job-month)
    if revenue_allocation == "cost":
        w = fact["total_cost"].clip(lower=0)
    else:
        w = fact["total_hours"].clip(lower=0)
    fact["_w"] = w

    denom = fact.groupby(["job_no", "month_key"])["_w"].transform("sum").replace({0: np.nan})
    fact["rev_allocated"] = fact["job_month_rev"] * (fact["_w"] / denom)
    fact["rev_allocated"] = fact["rev_allocated"].fillna(0.0)

    # --- profitability ---
    fact["gross_margin"] = fact["rev_allocated"] - fact["total_cost"]
    fact["gm_pct"] = np.where(fact["rev_allocated"] != 0, fact["gross_margin"] / fact["rev_allocated"], np.nan)

    # --- quotes join (optional) ---
    if quotes is not None and len(quotes) > 0:
        q = quotes.copy()
        q["job_no"] = q[cols.q_job_no].map(clean_job_no)
        if cols.q_task in q.columns:
            q["task_name"] = q[cols.q_task].map(clean_task_name)
        else:
            q["task_name"] = ""

        q["quoted_hours"] = pd.to_numeric(q.get(cols.q_quoted_hours, np.nan), errors="coerce")
        q["quoted_rate"] = pd.to_numeric(q.get(cols.q_quoted_rate, np.nan), errors="coerce")

        # If quotes are job-level (task empty), we keep them separately and apply in summaries.
        fact = fact.merge(
            q[["job_no", "task_name", "quoted_hours", "quoted_rate"]],
            on=["job_no", "task_name"],
            how="left",
            suffixes=("", "_q"),
        )
    else:
        fact["quoted_hours"] = np.nan
        fact["quoted_rate"] = np.nan

    # --- summaries ---
    job_task_summary = fact.groupby(["job_no", "task_name"], dropna=False).agg(
        actual_hours=("total_hours", "sum"),
        actual_cost=("total_cost", "sum"),
        actual_rev=("rev_allocated", "sum"),
        gross_margin=("gross_margin", "sum"),
        quoted_hours=("quoted_hours", "sum"),
    ).reset_index()

    job_task_summary["gm_pct"] = np.where(job_task_summary["actual_rev"] != 0, job_task_summary["gross_margin"]/job_task_summary["actual_rev"], np.nan)
    job_task_summary["hour_variance"] = job_task_summary["actual_hours"] - job_task_summary["quoted_hours"]
    job_task_summary["is_unquoted_task"] = job_task_summary["quoted_hours"].isna() | (job_task_summary["quoted_hours"] == 0)

    job_month_summary = fact.groupby(["job_no", "month_key"], dropna=False).agg(
        rev=("rev_allocated", "sum"),
        cost=("total_cost", "sum"),
        hours=("total_hours", "sum"),
        gm=("gross_margin", "sum"),
    ).reset_index()
    job_month_summary["gm_pct"] = np.where(job_month_summary["rev"] != 0, job_month_summary["gm"]/job_month_summary["rev"], np.nan)

    # --- QA tables ---
    qa = {}
    qa["missing_job_no"] = fact[fact["job_no"] == ""].copy()
    qa["missing_month_key"] = fact[fact["month_key"].isna()].copy()
    qa["hours_gt0_cost_eq0"] = fact[(fact["total_hours"] > 0) & (fact["total_cost"] == 0)].copy()

    return FactOutputs(
        fact_job_task_month=fact.drop(columns=["_w"], errors="ignore"),
        job_month_summary=job_month_summary,
        job_task_summary=job_task_summary,
        qa=qa,
    )
