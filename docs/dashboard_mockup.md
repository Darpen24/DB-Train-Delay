# Dashboard Mockup and Screenshot Plan

Use these views as portfolio screenshots after running:

```bash
python scripts/run_local_pipeline.py
streamlit run dashboard/app.py
```

## Screenshot 1: Main Reliability Overview

Show:

- KPI cards for route count, average delay, delay frequency, and cancellation rate
- bar chart of average delay by route
- scatter chart of delay per 100 km

Suggested filename:

```text
docs/images/dashboard_overview.png
```

## Screenshot 2: ICE vs Regional Filter

In the sidebar, select only:

- `ice`
- `regional`

Show the charts and route table.

Suggested filename:

```text
docs/images/ice_vs_regional.png
```

## Screenshot 3: AWS Evidence

After deploying the cloud version, capture:

- S3 bucket with `raw/`, `bronze/`, `silver/`, and `gold/`
- Athena query result for `fct_route_reliability`
- dbt docs lineage graph

