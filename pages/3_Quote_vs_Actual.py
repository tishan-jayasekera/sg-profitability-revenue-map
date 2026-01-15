import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.metrics.drivers import overrun_tasks, unquoted_work

st.title("Quote vs actual")

out = st.session_state.get("jp_out")
if out is None:
    st.info("Go to the main page and upload a workbook first.")
    st.stop()

jt = out.job_task_summary.copy()

st.subheader("Largest overruns (task-level)")
ov = overrun_tasks(jt, min_quoted_hours=1.0, n=25)
st.dataframe(ov, use_container_width=True)

st.subheader("Largest unquoted work (actual hours with no quote)")
uq = unquoted_work(jt, n=25)
st.dataframe(uq, use_container_width=True)

st.subheader("Quote accuracy scatter (quoted vs actual hours)")
df = jt.copy()
df["quoted_hours"] = pd.to_numeric(df["quoted_hours"], errors="coerce").fillna(0.0)
df = df[df["quoted_hours"] > 0].copy()
fig = px.scatter(df, x="quoted_hours", y="actual_hours", hover_data=["job_no","task_name"])
fig.add_shape(type="line", x0=0, y0=0, x1=df["quoted_hours"].max(), y1=df["quoted_hours"].max())
st.plotly_chart(fig, width="stretch")
