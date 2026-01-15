import streamlit as st

from src.io.loaders import load_workbook
from src.transform.build_fact_table import build_fact_tables
from src.config import ColumnMap

st.set_page_config(page_title="Job Profitability", page_icon="📈", layout="wide")

st.title("📈 Job Profitability — Quote → Execution")
st.caption("Upload your workbook and analyse where margin is being eroded (overruns, rate leakage, unquoted work).")

with st.sidebar:
    st.header("Inputs")
    file = st.file_uploader("Upload Excel workbook", type=["xlsx", "xls"])

    st.divider()
    st.header("Pipeline options")
    alloc = st.selectbox("Revenue allocation", ["hours", "cost"], index=0,
                         help="How to allocate monthly Rev Rec down to job-task (hours share vs cost share).")

    st.divider()
    st.header("Column mapping")
    st.caption("Defaults match your current sheet naming. Adjust later if needed.")
    # Keep mapping hidden for MVP; expose in next iteration.
    cols = ColumnMap()

if not file:
    st.info("Upload an Excel workbook to begin.")
    st.stop()

wb = load_workbook(file.getvalue())

if "timesheet" not in wb:
    st.error("Could not detect a Timesheet/WFM sheet in the workbook. Rename the sheet to include 'WFM' or 'Timesheet'.")
    st.dataframe(wb["_meta"])
    st.stop()

ts = wb.get("timesheet")
rr = wb.get("revrec")
q = wb.get("quotes")

@st.cache_data(show_spinner="Building fact tables...")
def run_pipeline(ts, rr, q, alloc):
    out = build_fact_tables(ts, rr, q, revenue_allocation=alloc, cols=ColumnMap())
    return out

out = run_pipeline(ts, rr, q, alloc)

# Share across pages
st.session_state["jp_out"] = out
st.session_state["jp_meta"] = wb.get("_meta")

st.success("Data loaded. Use the pages in the left sidebar to explore.")
st.write("Detected sheets:")
st.dataframe(st.session_state["jp_meta"], use_container_width=True)
