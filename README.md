# PitWall — F1 Race Intelligence Pipeline

An end-to-end data engineering project that ingests Formula 1 timing data, 
models it into an analytics warehouse, and serves a season analytics dashboard.

## Problem description

Formula 1 generates rich timing data every race weekend: lap times, tyre 
compounds, pit stops, weather, but it's locked inside APIs and scattered 
sources. There's no accessible way to ask questions like "how did the 2024 
title race unfold round by round?", "which compounds degrade fastest?", or 
"at which circuits does pole position actually matter?"

PitWall solves this by building a complete data platform: automated ingestion 
of five seasons of F1 data (2021–2025, plus the ongoing 2026 season), a 
dimensional warehouse in BigQuery with validated championship standings, and 
a four-page analytics dashboard covering standings, driver performance, race 
strategy, and circuit patterns.

## Architecture

FastF1 API → Python ingestion → GCS (raw parquet) → BigQuery (raw) 
→ dbt (staging → marts) → Looker Studio dashboard

Orchestrated by Kestra · Infrastructure managed with Terraform

[architecture diagram image here]

## Tech stack

- **Data source:** FastF1 (F1 timing data, 2018 onwards)
- **Ingestion:** Python (pandas, google-cloud-bigquery, google-cloud-storage)
- **Data lake:** Google Cloud Storage (Parquet)
- **Warehouse:** BigQuery
- **Transformations:** dbt Core (staging + mart layers, tests, documentation)
- **Orchestration:** Kestra (Dockerised, scheduled + parameterised flows)
- **IaC:** Terraform
- **Dashboard:** Looker Studio

## Warehouse design

Raw tables land unmodified from FastF1. dbt builds two layers:

**Staging** (views): type casting, renaming, deduplication via row_number() 
window functions — protecting downstream models from re-ingestion duplicates.

**Marts** (tables): analytics-ready models including cumulative championship 
standings (window functions over rounds), tyre stints derived from lap-level 
compound data (gaps-and-islands), and circuit-level aggregates.

### Partitioning and clustering

`mart_lap_times` (~103k rows) and `mart_race_results` are partitioned by 
season (integer range) and clustered by driver/round. Dashboard queries 
always filter by season and usually by driver — the partition prunes to one 
season's data and clustering skips irrelevant blocks within it. Smaller marts 
(standings, calendar) are left unpartitioned deliberately: below ~1GB the 
metadata overhead outweighs any pruning benefit.

## Data quality and validation

- Deduplication in staging guards against duplicate ingestion
- dbt tests: not_null, unique, accepted_values on key columns
- `ingestion/validate_completeness.py` reconciles loaded rounds against 
  expected rounds per season and exits non-zero on gaps
- Championship standings verified against official results across five 
  seasons (e.g. Verstappen 2024: 399 pipeline points + 38 sprint points 
  = 437 official)

### Known limitations

- Sprint sessions are not ingested; standings for sprint-era seasons run 
  below official totals by the sprint points amount (documented and verified)
- Kestra runs locally via Docker — scheduled flows execute only while the 
  host machine is running; production deployment would host Kestra on a VM
- FastF1 rate limits (500 calls/hour) require pacing during bulk loads

## Dashboard



## Reproducing this project

### Prerequisites
- Python 3.10+, Docker, Terraform
- A GCP project with BigQuery and Cloud Storage APIs enabled
- A service account with BigQuery Admin and Storage Admin roles 
  (created manually — see note below)

### Setup
1. Clone the repo and install dependencies:
   pip install -r requirements.txt
2. Copy terraform/terraform.tfvars.example to terraform.tfvars, fill in 
   your project ID, bucket name, and key path
3. Provision infrastructure:
   cd terraform && terraform init && terraform apply
4. Create a .env file (see .env.example)
5. Verify setup: python ingestion/test_fastf1.py
6. Historical load: python ingestion/ingest_historical.py 
   (several hours due to API rate limits)
7. Validate: python ingestion/validate_completeness.py
8. Build models: cd dbt/pitwall_dbt && dbt run && dbt test
9. Orchestration: cd orchestration && docker compose up -d, then create 
   the flows from orchestration/flows/ in the Kestra UI

Note on IAM: the pipeline service account is provisioned manually with 
least-privilege roles rather than granting Terraform IAM-management 
permissions.

## Project structure
```
PitWall-F1-Race-Intelligence-Dashboard/
├── ingestion/
│   ├── ingest_session.py           # Core ingestion: one session → GCS + BigQuery
│   ├── ingest_race_weekend.py      # CLI: ingest Q + R for a given season/round
│   ├── ingest_latest.py            # Auto-detects and ingests the latest completed round
│   ├── ingest_historical.py        # Bulk historical load across seasons
│   ├── validate_completeness.py    # Reconciles loaded rounds against expected per season
│   ├── create_tables.py            # Creates raw BigQuery tables
│   ├── schemas.py                  # Raw table schema definitions
│   └── test_fastf1.py              # Setup smoke test
├── dbt/
│   └── pitwall_dbt/
│       ├── dbt_project.yml
│       └── models/
│           ├── staging/            # Views: typing, renaming, deduplication
│           │   ├── sources.yml     # Raw source definitions + column docs
│           │   ├── schema.yml      # Model tests and documentation
│           │   └── stg_*.sql       # sessions, results, laps, pit_stops, weather, drivers, circuits
│           └── mart/               # Tables: analytics-ready models
│               ├── mart_race_results.sql
│               ├── mart_driver_standings.sql       # Cumulative points via window functions
│               ├── mart_final_standings.sql
│               ├── mart_constructor_standings.sql
│               ├── mart_lap_times.sql              # Partitioned by season, clustered by driver
│               ├── mart_tyre_strategy.sql          
│               ├── mart_pit_stops.sql
│               ├── mart_qualifying_results.sql
│               ├── mart_season_calendar.sql
│               └── mart_circuit_stats.sql
├── orchestration/
│   ├── docker-compose.yml          
│   └── flows/
│       ├── pitwall_race_weekend.yml     
│       └── pitwall_scheduled_ingest.yml 
├── terraform/
│   ├── main.tf                    
│   ├── variables.tf
│   └── terraform.tfvars.example
├── requirements.txt
├── .env.example
└── README.md
```
