from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def trend_job_margin(job_month_summary: pd.DataFrame) -> go.Figure:
    df = job_month_summary.copy()
    df["month_key"] = pd.to_datetime(df["month_key"], errors="coerce")
    df = df.sort_values("month_key")
    by_m = df.groupby("month_key", dropna=False).agg(rev=("rev", "sum"), gm=("gm", "sum")).reset_index()
    fig = px.line(by_m, x="month_key", y=["rev", "gm"], markers=True)
    fig.update_layout(legend_title_text="", xaxis_title="", yaxis_title="")
    return fig

def bar_top_loss_jobs(loss_jobs: pd.DataFrame) -> go.Figure:
    df = loss_jobs.copy()
    fig = px.bar(df, x="gm", y="job_no", orientation="h")
    fig.update_layout(xaxis_title="Gross margin ($)", yaxis_title="Job")
    return fig
