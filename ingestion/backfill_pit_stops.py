import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fastf1
import time
from google.cloud import bigquery
from dotenv import load_dotenv
from ingest_session import (
    extract_pit_stops, upload_to_gcs,
    load_to_bigquery, bq_client, PROJECT_ID, RAW_DATASET
)
from datetime import datetime, timezone

load_dotenv()
fastf1.Cache.enable_cache('cache/')

def get_all_sessions():
    query = f"""
        SELECT session_id, season, round_number, session_type
        FROM `{PROJECT_ID}.{RAW_DATASET}.raw_sessions`
        ORDER BY season, round_number
    """
    return list(bq_client.query(query).result())

def backfill():
    sessions = get_all_sessions()
    print(f"Backfilling pit stops for {len(sessions)} sessions...")

    for row in sessions:
        session_id = row.session_id
        season = row.season
        round_number = row.round_number
        session_type = row.session_type

        # Only races have pit stops
        if session_type != 'R':
            print(f"Skipping {session_id} — not a race session")
            continue

        try:
            print(f"Processing {session_id}...")
            session = fastf1.get_session(season, round_number, session_type)
            session.load(laps=True, telemetry=False, weather=False)
            loaded_at = datetime.now(timezone.utc)

            pit_df = extract_pit_stops(session.laps.copy(), session_id, loaded_at)
            if pit_df is not None:
                upload_to_gcs(pit_df, f"pit_stops/{session_id}.parquet")
                load_to_bigquery(pit_df, "raw_pit_stops")
                print(f"Loaded {len(pit_df)} rows into raw_pit_stops for {session_id}")
            
            time.sleep(15)

        except Exception as e:
            print(f"Failed {session_id}: {e}")
            time.sleep(10)
            continue

    print("Backfill complete.")

if __name__ == "__main__":
    backfill()