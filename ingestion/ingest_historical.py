import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time

from ingest_race_weekend import main as ingest_weekend
from ingest_session import ingest_session
import fastf1

# Number of rounds per season
SEASON_ROUNDS = {
    2021: 22,
    2022: 22,
    2023: 22,
    2024: 24,
    2025: 24,
}

def ingest_historical():
    for season, total_rounds in SEASON_ROUNDS.items():
        print(f"\n{'='*40}")
        print(f"Starting season {season} — {total_rounds} rounds")
        print(f"{'='*40}")

        for round_number in range(1, total_rounds + 1):
            print(f"\nSeason {season} — Round {round_number}/{total_rounds}")
            for session_type in ['Q', 'R']:
                try:
                    ingest_session(season, round_number, session_type)
                    time.sleep(30)  # wait 30 seconds between sessions
                except Exception as e:
                    print(f"  Skipped {season} R{round_number} {session_type}: {e}")
                    time.sleep(10)  # shorter wait on failure
                    continue

    print("\nHistorical ingestion complete.")

if __name__ == "__main__":
    ingest_historical()