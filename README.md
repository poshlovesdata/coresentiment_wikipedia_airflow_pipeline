# CoreSentiment - Wikipedia Pageviews ETL with Apache Airflow

This project implements a simple, runnable data pipeline using Apache Airflow to ingest one hour of Wikimedia pageviews, extract counts for five companies (Amazon, Apple, Facebook, Google, Microsoft), load the results into a PostgreSQL database, and report execution details via email.

The pipeline is designed to reinforce practical data workflow orchestration concepts: scheduling, retries, idempotence, failure alerts, data extraction/processing, and loading.

## Architecture Overview

![Pipeline Architecture](/doc_images/coresentiment-arch.png)

- Source: Wikimedia pageviews hourly dump in gzip format.
- Orchestration: Apache Airflow DAG with standard Bash and Python operators.
- Processing:
  - Download and decompress a selected hourly dump.
  - Filter pageview entries for the five target companies.
  - Write filtered rows to CSV.
- Storage: PostgreSQL (configurable via environment).
- Observability: Email alerts on task failure, success summary email on pipeline completion with duration.

## Data Source

- Index of pageviews: https://dumps.wikimedia.org/other/pageviews/
- Hourly files: `https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/pageviews-{year}{month}{day}-{hour}0000.gz`
  - Example for October 10, 2025 at 09:00–10:00: `pageviews-20251010-100000.gz` (filename timestamp refers to the end of the hour window).
- File format (space-delimited):
  1. Domain code (e.g., `en`, `en.m`)
  2. Page title (e.g., `Amazon`)
  3. View count (integer)
  4. Response size in bytes

## DAG: `wiki_etl_pipeline`

Location: `dags/wiki_etl_pipeline_dag.py`

- Schedule: `@daily`
- Start date: 2025-10-22
- Catchup: disabled
- Default args:
  - Retries: `2`
  - Retry delay: `5 minutes`
  - Failure callback: emails details and a link to logs

### Tasks

- `record_start_time` (Python): captures start timestamp (for duration computation).
- `download_wiki` (Bash): downloads and decompresses one hourly pageviews file; outputs unzipped file path via stdout (captured by Airflow XCom).
- `transform_txt` (Python): reads unzipped text file, filters for the five companies, writes CSV to `output/filtered_wiki_pages.csv`.
- `load_db` (Python): loads CSV into PostgreSQL table `wiki_views`.
- `record_end_time` (Python): captures end timestamp and publishes `duration` to XCom.
- `send_notification` (Email): sends success summary email including run date and duration.

## Repository Layout

- `dags/wiki_etl_pipeline_dag.py` — Airflow DAG and task definitions.
- `scripts/bash/download_file.sh` — Bash script to download and unzip a Wikimedia hourly dump.
- `scripts/python/process_txt.py` — Transforms pageviews text file to a filtered CSV for the five companies.
- `scripts/python/load_database.py` — Loads the filtered CSV into PostgreSQL.
- `scripts/python/utils.py` — Utility functions for recording duration and failure alert email.
- `docker-compose.yaml` — Container composition for Airflow (webserver, scheduler, etc.).
- `requirements.txt` — Python dependencies for the pipeline.

## Configuration

Create a `.env` file (mounted into the Airflow containers) with:

- `FROM_EMAIL` — sender email address for notifications.
- `CLOUD_POSTGRES_URL` — SQLAlchemy-style PostgreSQL URL for the pipeline’s target database.
- `POSTGRES_USER` — Airflow metadata database username.
- `POSTGRES_PASSWORD` — Airflow metadata database password.
- `POSTGRES_DB` — Airflow metadata database name.
- `POSTGRES_PORT` — Airflow metadata database port.
- `POSTGRES_HOST` — Airflow metadata database host.
- `_AIRFLOW_WWW_USER_USERNAME` — Airflow UI admin username.
- `_AIRFLOW_WWW_USER_PASSWORD` — Airflow UI admin password.

Notes:
- `POSTGRES_*` variables configure the Airflow metadata database (internal Airflow storage), not the pipeline’s analytical data store.
- The pipeline loads filtered pageviews into the database specified by `CLOUD_POSTGRES_URL`.

Airflow connection required:

- `smtp_conn` — SMTP connection used by `EmailOperator` for notifications.

Example `.env`:

```env
FROM_EMAIL=you@example.com
CLOUD_POSTGRES_URL=postgresql+psycopg2://user:password@postgres:5432/coresentiment_db
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
POSTGRES_PORT=5432
POSTGRES_HOST=postgres
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
```

## Customizing Hour and Date

Update the hourly dump URL in `scripts/bash/download_file.sh`:

- Variable: `wiki_url`
- Pattern: `https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/pageviews-{year}{month}{day}-{hour}0000.gz`
- Ensure the timestamp reflects the end of the hour window (data for 09:00–10:00 uses `100000`).

## Running Locally

1. Ensure Docker and Docker Compose are installed.
2. Populate `.env` with the variables you already have in your environment  and place it in the root directory.
3. Build and start the Airflow stack (refer to your existing `docker-compose.yaml`). Typical commands are:
   - `docker compose up --build -d`
4. Access the Airflow UI (usually `http://localhost:8080`) and enable the `wiki_etl_pipeline` DAG.
5. Trigger a run manually to verify.

## Database Output

- Table: `wiki_views`
- Columns: `project` (domain code), `page_title`, `view_count` (string parsed from file)

SQL to find the company with the highest pageviews in the loaded hour:

```sql
SELECT page_title, MAX(CAST(view_count AS INTEGER)) AS max_views
FROM wiki_views
GROUP BY page_title
ORDER BY max_views DESC
LIMIT 1;
```
![Query Result](/doc_images/db_output.png)


Depending on the exact input data for the chosen hour, this returns the top-viewed company among the five.

## Operational Concerns
![DAG Success](/doc_images/airflow_sucess.jpg)
![DAG Failure](/doc_images/airflow_failure.jpg)

- Retries: Tasks retry automatically on transient failures.
- Idempotence: Each run overwrites previous artifacts in `output/` and replaces the `wiki_views` table; runs are deterministic for a given input hour.
- Failure Alerts: A task-level `on_failure_callback` sends detailed email with a log link.
- Observability: Success email includes run date and total duration sourced from XCom.

## Dependencies

See `requirements.txt`:

- `pandas`
- `sqlalchemy`
- `psycopg2-binary`
- `python-dotenv`

## Options

- Configure hour/date in `scripts/bash/download_file.sh` by editing `YEAR`, `MONTH`, `DAY`, and `END_HOUR`.
