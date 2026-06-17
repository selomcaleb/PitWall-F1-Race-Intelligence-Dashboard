from google.cloud import bigquery
from dotenv import load_dotenv
import os
from schemas import (
    RAW_SESSIONS_SCHEMA, RAW_RESULTS_SCHEMA, RAW_LAPS_SCHEMA,
    RAW_PIT_STOPS_SCHEMA, RAW_WEATHER_SCHEMA, RAW_DRIVERS_SCHEMA,
    RAW_CIRCUITS_SCHEMA
)

load_dotenv()

client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))
dataset = os.getenv("BQ_RAW_DATASET")

def create_table(table_name, schema):
    table_id = f"{os.getenv('GCP_PROJECT_ID')}.{dataset}.{table_name}"
    schema_fields = [
        bigquery.SchemaField(col["name"], col["type"]) for col in schema
    ]
    table = bigquery.Table(table_id, schema=schema_fields)
    try:
        client.create_table(table)
        print(f"Created table {table_name}")
    except Exception as e:
        print(f"Table {table_name} already exists or error: {e}")

create_table("raw_sessions", RAW_SESSIONS_SCHEMA)
create_table("raw_results", RAW_RESULTS_SCHEMA)
create_table("raw_laps", RAW_LAPS_SCHEMA)
create_table("raw_pit_stops", RAW_PIT_STOPS_SCHEMA)
create_table("raw_weather", RAW_WEATHER_SCHEMA)
create_table("raw_drivers", RAW_DRIVERS_SCHEMA)
create_table("raw_circuits", RAW_CIRCUITS_SCHEMA)