from dataclasses import dataclass

@dataclass(frozen=True)
class ColumnMap:
    # WFM / Timesheet
    ts_job_no: str = "[Job] Job No."
    ts_task: str = "[Job Task] Name"
    ts_date: str = "[Time] Date"
    ts_hours: str = "[Time] Actual Hrs"
    ts_bill_rate: str = "Billable Rate"
    ts_base_rate: str = "Base Rate"
    ts_quoted_rate: str = "Quoted Rate"
    ts_month_key: str = "Month Key"  # optional; if absent we derive from ts_date

    # Rev Rec
    rr_job_no: str = "[Job] Job No."
    rr_month_key: str = "MonthKey"   # expected as first-of-month date, or any date within month
    rr_amount: str = "Amount"

    # Quotes / Estimates (optional)
    q_job_no: str = "[Job] Job No."
    q_task: str = "[Job Task] Name"  # optional; if missing treat as job-level quote
    q_quoted_hours: str = "Quoted Hours"
    q_quoted_rate: str = "Quoted Rate"
    q_quote_date: str = "Quote Date" # optional
