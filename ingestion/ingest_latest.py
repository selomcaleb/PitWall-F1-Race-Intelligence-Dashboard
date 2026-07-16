import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fastf1
import pandas as pd
from datetime import datetime, timezone
from ingest_session import ingest_session

cache_dir = os.getenv("FASTF1_CACHE_DIR", "cache/")
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)


def find_latest_completed_round(season):
    """Return the most recent round whose race date has passed, or None."""
    schedule = fastf1.get_event_schedule(season, include_testing=False)
    now = pd.Timestamp.now(tz="UTC")

    completed = schedule[
        pd.to_datetime(schedule["EventDate"], utc=True) < now
    ]

    if completed.empty:
        return None

    return int(completed["RoundNumber"].max())


def main():
    season = datetime.now(timezone.utc).year
    latest_round = find_latest_completed_round(season)

    if latest_round is None:
        print(f"No completed rounds yet in {season}. Nothing to ingest.")
        return

    print(f"Latest completed round in {season}: {latest_round}")

    for session_type in ['Q', 'R']:
        try:
            ingest_session(season, latest_round, session_type)
        except Exception as e:
            print(f"Failed to ingest {session_type}: {e}")


if __name__ == "__main__":
    main()