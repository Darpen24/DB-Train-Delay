# Interview Notes

## What This Project Demonstrates

- API-first ingestion with graceful retry handling
- raw to bronze to silver to gold modeling discipline
- local execution path plus AWS-oriented deployment design
- dbt test coverage and CI checks
- operational metrics, not just visualization

## Design Decisions To Talk Through

- Raw records are preserved so transforms can be replayed when business logic changes.
- Reliability is modeled as a weighted score instead of a single delay metric because cancellations and platform changes matter operationally.
- The sample project uses a small local dataset, but the Spark and AWS structure is designed for scale-out execution.
- Source freshness is modeled in dbt using `ingested_at`; in production this should come from the ingestion timestamp written with each API batch.

## Honest Limitations

- The current dataset shows observed disruption patterns, not root-cause labels such as weather or infrastructure failures.
- The live `transport.rest` endpoint returned HTTP `503` during one validation attempt, which is realistic and is why retry logic and raw persistence are included.
- The AWS resources are scaffolded and validated in code, but not deployed from this repo without user-provided AWS credentials and bucket names.

## Strong Follow-Up Ideas

- Persist remarks and disruption messages from live APIs for cause analysis.
- Add scheduled ingestion and multi-day trend tracking.
- Publish Athena-backed dbt marts and a hosted dashboard.
