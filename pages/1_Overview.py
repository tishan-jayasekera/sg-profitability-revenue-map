import streamlit as st
import pandas as pd

from src.metrics.drivers import top_loss_jobs
from src.viz.charts import trend_job_margin, bar_top_loss_jobs

st.title("Overview")

out = st.session_state.get("jp_out")
if out is None:
    st.info("Go to the main page and upload a workbook first.")
    st.stop()

jm = out.job_month_summary
jt = out.job_task_summary

# KPIs
total_rev = float(pd.to_numeric(jm["rev"], errors="coerce").fillna(0).sum())
total_cost = float(pd.to_numeric(jm["cost"], errors="coerce").fillna(0).sum())
total_gm = float(pd.to_numeric(jm["gm"], errors="coerce").fillna(0).sum())
gm_pct = (total_gm / total_rev) if total_rev else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue (allocated)", f"${total_rev:,.0f}")
c2.metric("Cost", f"${total_cost:,.0f}")
c3.metric("Gross margin", f"${total_gm:,.0f}")
c4.metric("GM %", f"{gm_pct:.1%}" if gm_pct is not None else "—")

st.subheader("Trend (all jobs)")
st.plotly_chart(trend_job_margin(jm), width="stretch")

st.subheader("Top loss-making jobs")
loss = top_loss_jobs(jm, n=20)
st.plotly_chart(bar_top_loss_jobs(loss), width="stretch")
st.dataframe(loss, use_container_width=True)
