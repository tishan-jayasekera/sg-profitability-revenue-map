# Job Profitability (Quote → Execution) — Streamlit App

This repo is an MVP scaffold for analysing **job profitability from quotation to execution** using:
- **WFM timesheets** (daily)
- **Revenue Recognition** (monthly)
- **Quotes / estimates** (job and/or job-task level)

It builds a canonical **job_task_month fact table**, then produces job-level summaries, quote-vs-actual variance views,
and driver diagnostics (overruns, rate leakage, unquoted work, missing data flags).

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

## Data inputs

Upload a single Excel workbook (recommended) containing some/all of these sheets:
- `WFM` (or `Timesheet`) — daily timesheets
- `Rev Rec` (or `Revenue`) — monthly revenue recognition
- `Quotes` (or `Estimates`) — quote hours/rates (optional but strongly recommended)

The loader uses **best-effort sheet name detection** (see `src/io/loaders.py`).

## Outputs (in-app)

- Overview KPIs (Revenue / Cost / Margin, loss-makers, trends)
- Job drilldown (task mix, rate/cost leakage, timeseries)
- Quote vs actual (accuracy, overruns, unquoted work)
- Drivers & diagnostics (where margin is being eroded)
- Data QA (missing rates, unmatched jobs, duplicate keys)

## Notes

This is a **scaffold**. Plug your current notebook logic into:
- `src/transform/build_fact_table.py`
- `src/metrics/*`

so the app is just a UI over a clean, testable pipeline.
