import fastf1
import sys
from pathlib import Path


def pull_historical_data(year:int, gp:str, session_type:str):
    """
        function pulls historical F1 session lap data using FastF1 and saves to a csv file
        @params:
            year : int
                The season year (e.g., 2023)
            gp : str
                Grand Prix name as recognized by FastF1 (e.g., "Bahrain", "Monaco")
            session_type : str
                Session type (e.g., "Race", "Qualifying", "FP1")
    """

    base_dir = Path(__file__).resolve().parents[1]
    cache_dir = base_dir / "data" / "cache"
    raw_dir = base_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # save to cache
    fastf1.Cache.enable_cache(str(cache_dir))

    # load session
    print(f"Loading session: {year} {gp} {session_type}")
    session = fastf1.get_session(year, gp, session_type)
    session.load()

    # extract lap data and save to csv
    laps = session.laps

    if laps is None or laps.empty:
        print("No lap data found. Exiting.")
        return

    # check all laps and drivers loaded
    print(f"Loaded laps: {len(laps)}")
    print(f"Drivers: {laps['Driver'].nunique() if 'Driver' in laps.columns else 'Unknown'}")


    # Save to CSV
    gp_clean = gp.lower().replace(" ", "_")
    session_clean = session_type.lower()

    filename = f"{year}_{gp_clean}_{session_clean}.csv"
    output_path = raw_dir / filename
    laps.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")






if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python pull_data.py <year> <gp> <session>")
        print("Example: python pull_data.py 2026 Monaco Race") 
        sys.exit(1)

    pull_historical_data(int(sys.argv[1]), sys.argv[2], sys.argv[3])


