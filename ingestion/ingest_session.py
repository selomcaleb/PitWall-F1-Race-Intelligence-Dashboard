import fastf1
import pandas as pd
from google.cloud import bigquery, storage
from dotenv import load_dotenv
import os
from datetime import datetime
import pyarrow
from datetime import timezone

load_dotenv()

fastf1.Cache.enable_cache('cache/')

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
RAW_DATASET = os.getenv("BQ_RAW_DATASET")

bq_client = bigquery.Client(project=PROJECT_ID)
gcs_client = storage.Client(project=PROJECT_ID)


def upload_to_gcs(df, blob_name):
    """Save dataframe as parquet to GCS."""
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(df.to_parquet(index=False), content_type="application/octet-stream")
    print(f"Uploaded {blob_name} to GCS")


def load_to_bigquery(df, table_name):
    """Load dataframe into BigQuery table."""
    table_id = f"{PROJECT_ID}.{RAW_DATASET}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=False,
    )
    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows into {table_name}")


def check_already_loaded(session_id):
    """Check if this session has already been loaded."""
    query = f"""
        SELECT COUNT(*) as count 
        FROM `{PROJECT_ID}.{RAW_DATASET}.raw_sessions`
        WHERE session_id = '{session_id}'
    """
    result = bq_client.query(query).result()
    for row in result:
        return row.count > 0
    return False


def build_session_id(season, round_number, session_type):
    return f"{season}_{round_number}_{session_type}"

def extract_pit_stops(laps, session_id, loaded_at):
    pit_laps = laps[laps["PitInTime"].notna()].copy()
    if pit_laps.empty:
        print("No pit stop data found for this session.")
        return None
    pit_laps["session_id"] = session_id
    pit_laps["loaded_at"] = loaded_at
    pit_laps["pit_duration_seconds"] = (
        pit_laps["PitOutTime"] - pit_laps["PitInTime"]
    ).dt.total_seconds()
    pit_df = pit_laps[[
        "session_id", "DriverNumber", "Driver", "LapNumber",
        "pit_duration_seconds", "loaded_at"
    ]].copy()
    pit_df.columns = [
        "session_id", "driver_number", "abbreviation",
        "lap_number", "pit_duration_seconds", "loaded_at"
    ]
    pit_df["stop_number"] = pit_df.groupby("driver_number").cumcount() + 1
    return pit_df

def ingest_session(season, round_number, session_type='R'):
    session_id = build_session_id(season, round_number, session_type)

    if check_already_loaded(session_id):
        print(f"Session {session_id} already loaded. Skipping.")
        return

    print(f"Loading session {session_id}...")
    session = fastf1.get_session(season, round_number, session_type)
    session.load()

    loaded_at = datetime.now(timezone.utc)

    # SESSIONS
    session_df = pd.DataFrame([{
        "session_id": session_id,
        "season": season,
        "round_number": round_number,
        "country": session.event.get("Country", ""),
        "location": session.event.get("Location", ""),
        "circuit_key": str(session.event.get("OfficialEventName", "")),
        "session_type": session_type,
        "session_date": session.date.date(),
        "loaded_at": loaded_at,
    }])
    upload_to_gcs(session_df, f"sessions/{session_id}.parquet")
    load_to_bigquery(session_df, "raw_sessions")

    # RESULTS
    results = session.results.copy()
    results["session_id"] = session_id
    results["loaded_at"] = loaded_at
    results_df = results[[
        "session_id", "DriverNumber", "Abbreviation", "FullName",
        "TeamName", "GridPosition", "Position", "Points",
        "Status", "Time", "loaded_at"
    ]].copy()
    results_df.columns = [
        "session_id", "driver_number", "abbreviation", "full_name",
        "team_name", "grid_position", "finish_position", "points",
        "status", "time", "loaded_at"
    ]
    results_df["time"] = results_df["time"].astype(str)
    results_df["grid_position"] = pd.to_numeric(results_df["grid_position"], errors="coerce")
    results_df["finish_position"] = pd.to_numeric(results_df["finish_position"], errors="coerce")
    upload_to_gcs(results_df, f"results/{session_id}.parquet")
    load_to_bigquery(results_df, "raw_results")

    # LAPS
    laps = session.laps.copy()
    laps["session_id"] = session_id
    laps["loaded_at"] = loaded_at
    laps["lap_time_seconds"] = laps["LapTime"].dt.total_seconds()
    laps["sector_1_seconds"] = laps["Sector1Time"].dt.total_seconds()
    laps["sector_2_seconds"] = laps["Sector2Time"].dt.total_seconds()
    laps["sector_3_seconds"] = laps["Sector3Time"].dt.total_seconds()
    laps["pit_in_time_seconds"] = laps["PitInTime"].dt.total_seconds()
    laps["pit_out_time_seconds"] = laps["PitOutTime"].dt.total_seconds()
    laps_df = laps[[
        "session_id", "DriverNumber", "Driver", "LapNumber",
        "lap_time_seconds", "sector_1_seconds", "sector_2_seconds",
        "sector_3_seconds", "Compound", "TyreLife", "IsPersonalBest",
        "pit_in_time_seconds", "pit_out_time_seconds", "TrackStatus", "loaded_at"
    ]].copy()
    laps_df.columns = [
        "session_id", "driver_number", "abbreviation", "lap_number",
        "lap_time_seconds", "sector_1_seconds", "sector_2_seconds",
        "sector_3_seconds", "compound", "tyre_life", "is_personal_best",
        "pit_in_time_seconds", "pit_out_time_seconds", "track_status", "loaded_at"
    ]
    upload_to_gcs(laps_df, f"laps/{session_id}.parquet")
    load_to_bigquery(laps_df, "raw_laps")

    # WEATHER
    weather = session.weather_data.copy()
    weather["session_id"] = session_id
    weather["loaded_at"] = loaded_at
    weather_df = weather[[
        "session_id", "Time", "AirTemp", "TrackTemp",
        "Humidity", "Rainfall", "WindSpeed", "loaded_at"
    ]].copy()
    weather_df.columns = [
        "session_id", "timestamp", "air_temp", "track_temp",
        "humidity", "rainfall", "wind_speed", "loaded_at"
    ]
    weather_df["timestamp"] = (session.date + weather_df["timestamp"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    upload_to_gcs(weather_df, f"weather/{session_id}.parquet")
    load_to_bigquery(weather_df, "raw_weather")

    # DRIVERS
    drivers_df = session.results[[
        "DriverNumber", "Abbreviation", "FullName", "TeamName", "CountryCode"
    ]].copy()
    drivers_df.columns = [
    "driver_number", "abbreviation", "full_name", "team_name", "nationality"
    ]
    drivers_df["season"] = season
    drivers_df["loaded_at"] = loaded_at
    upload_to_gcs(drivers_df, f"drivers/{session_id}.parquet")
    load_to_bigquery(drivers_df, "raw_drivers")

    # CIRCUITS
    circuits_df = pd.DataFrame([{
        "circuit_key": str(session.event.get("OfficialEventName", "")),
        "circuit_name": session.event.get("Location", ""),
        "country": session.event.get("Country", ""),
        "location": session.event.get("Location", ""),
        "loaded_at": loaded_at,
    }])
    upload_to_gcs(circuits_df, f"circuits/{session_id}.parquet")
    load_to_bigquery(circuits_df, "raw_circuits")

    # PIT STOPS
    pit_df = extract_pit_stops(session.laps.copy(), session_id, loaded_at)
    if pit_df is not None:
        upload_to_gcs(pit_df, f"pit_stops/{session_id}.parquet")
        load_to_bigquery(pit_df, "raw_pit_stops")
        print(f"Loaded {len(pit_df)} rows into raw_pit_stops")

    print(f"Session {session_id} ingested successfully.")


if __name__ == "__main__":
    ingest_session(2024, 1, 'R')