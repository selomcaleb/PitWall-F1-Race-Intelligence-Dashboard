import numpy as np
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[0]
raw_dir = base_dir / "data" / "raw"
processed_dir = base_dir / "data" / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)


# Load csv 
laps_df = pd.read_csv(raw_dir / "2025_monaco_race.csv")

#rename  used columns
laps_df = laps_df.rename(columns={
    "Driver": "driver",
    "LapNumber": "lap",
    "Stint": "stint",
    "Compound": "compound",
    "LapTime": "lap_time",
    "Position": "position"
})

# keep only relevant cols
laps_df = laps_df[[
    "driver",
    "lap",
    "stint",
    "compound",
    "lap_time",
    "position"]]

 #Convert lap_time to seconds
laps_df["lap_time"] = pd.to_timedelta(laps_df["lap_time"], errors="coerce")
laps_df["lap_time"] = laps_df["lap_time"].dt.total_seconds()

# detect a pit stop
# sort by driver and lap this hepls in determining where a pit has happended
laps_df = laps_df.sort_values(by=["driver", "lap"]).reset_index(drop=True)
laps_df["prev_stint"] = laps_df.groupby("driver")["stint"].shift(1)

laps_df["pit_lap"] = (
    (laps_df["stint"] > laps_df["prev_stint"])
).astype(int)

# First lap should not count as pit
laps_df["pit_lap"] = laps_df["pit_lap"].fillna(0)


# compute tire age
laps_df["tire_age"] = laps_df.groupby(["driver", "stint"]).cumcount()

# rolling features
laps_df["rolling_lap_avg_3"] = (
    laps_df.groupby("driver")["lap_time"]
    .rolling(window=3, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

laps_df["lap_time_delta"] = laps_df["lap_time"] - laps_df["rolling_lap_avg_3"]


def compute_pit_labels(df, horizon=3):
    """
        function takes the row from data frame and detects pit stops.
        Why next pit in next 3 laps?
        We have to define a prediction horizon “How far into the future do we want to predict a pit stop?”

        @param:
            row: row from data frame
        @return:
            boolean: True or False
    """
    df["pit_next_3_laps"] = 0
    for driver, group in df.groupby("driver"):
        pit_laps = group[group["pit_lap"] == 1]["lap"].values

        for idx, row in group.iterrows():
            current_lap = row["lap"]

            if any((current_lap < pit <= current_lap + horizon) for pit in pit_laps):
                df.at[idx, "pit_next_3_laps"] = 1

    return df

laps_df = compute_pit_labels(laps_df)

# add race id
laps_df["race_id"] = "2025_monaco_race"

#create new dataframe with just the data needed
final_df = laps_df[[
    "race_id",
    "driver",
    "lap",
    "stint",
    "compound",
    "tire_age",
    "lap_time",
    "rolling_lap_avg_3",
    "lap_time_delta",
    "position",
    "pit_next_3_laps"
]]

#Saves processed dataset
output_path = processed_dir / "2025_monaco_processed.csv"
final_df.to_csv(output_path, index=False)
