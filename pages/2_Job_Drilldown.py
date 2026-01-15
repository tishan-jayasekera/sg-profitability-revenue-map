import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Job drilldown")

out = st.session_state.get("jp_out")
if out is None:
    st.info("Go to the main page and upload a workbook first.")
    st.stop()

fact = out.fact_job_task_month.copy()
fact["month_key"] = pd.to_datetime(fact["month_key"], errors="coerce")

jobs = sorted([j for j in fact["job_no"].dropna().unique() if str(j).strip() != ""])
job = st.selectbox("Select job", jobs)

df = fact[fact["job_no"] == job].copy()

# Job summary
rev = float(df["rev_allocated"].fillna(0).sum())
cost = float(df["total_cost"].fillna(0).sum())
gm = rev - cost
gm_pct = gm / rev if rev else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"${rev:,.0f}")
c2.metric("Cost", f"${cost:,.0f}")
c3.metric("Gross margin", f"${gm:,.0f}")
c4.metric("GM %", f"{gm_pct:.1%}" if gm_pct is not None else "—")

st.subheader("Task mix (by hours)")
task = df.groupby("task_name", dropna=False).agg(hours=("total_hours","sum"), gm=("gross_margin","sum")).reset_index()
fig = px.bar(task.sort_values("hours", ascending=False).head(30), x="hours", y="task_name", orientation="h")
st.plotly_chart(fig, width="stretch")

st.subheader("Monthly trend")
m = df.groupby("month_key", dropna=False).agg(rev=("rev_allocated","sum"), cost=("total_cost","sum")).reset_index().sort_values("month_key")
m["gm"] = m["rev"] - m["cost"]
fig2 = px.line(m, x="month_key", y=["rev","cost","gm"], markers=True)
st.plotly_chart(fig2, width="stretch")

st.subheader("Underlying fact table (job-task-month)")
st.dataframe(df.sort_values(["month_key","task_name"]), use_container_width=True)
