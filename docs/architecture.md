# Architecture

## Local Version

The local version is useful for development and interviews because it runs without cloud credentials.

```text
sample JSON or transport.rest API
  -> Python ingestion
  -> local raw JSON
  -> pandas/PySpark transformations
  -> local Parquet tables
  -> dbt models
  -> Streamlit dashboard
```

## AWS Version

```text
EventBridge schedule
  -> Lambda or containerized Python collector
  -> S3 raw zone
  -> Glue PySpark ETL
  -> S3 bronze/silver Parquet
  -> Glue Data Catalog
  -> Athena
  -> dbt-athena
  -> Power BI or Streamlit
```

## Data Layers

| Layer | Purpose | Format |
|---|---|---|
| Raw | Immutable API responses | JSON |
| Bronze | Parsed source-aligned events | Parquet |
| Silver | Clean typed analytical events | Parquet |
| Gold | Route reliability marts | Parquet or Athena tables |

## Key Design Choices

- Keep raw data immutable so API bugs or model changes can be replayed.
- Use PySpark for scalable transformation logic.
- Use dbt for analytical modeling, tests, lineage, and documentation.
- Use Athena as the serverless SQL layer over S3.
- Use Streamlit for a lightweight portfolio dashboard.

