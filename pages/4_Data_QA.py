import streamlit as st

st.title("Data QA")

out = st.session_state.get("jp_out")
if out is None:
    st.info("Go to the main page and upload a workbook first.")
    st.stop()

qa = out.qa

for name, df in qa.items():
    st.subheader(name.replace("_", " ").title())
    if df is None or len(df) == 0:
        st.success("No issues found.")
    else:
        st.warning(f"{len(df):,} rows flagged")
        st.dataframe(df.head(200), use_container_width=True)
