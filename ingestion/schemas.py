RAW_SESSIONS_SCHEMA = [
    {"name": "session_id", "type": "STRING"},
    {"name": "season", "type": "INTEGER"},
    {"name": "round_number", "type": "INTEGER"},
    {"name": "country", "type": "STRING"},
    {"name": "location", "type": "STRING"},
    {"name": "circuit_key", "type": "STRING"},
    {"name": "session_type", "type": "STRING"},
    {"name": "session_date", "type": "DATE"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]

RAW_RESULTS_SCHEMA = [
    {"name": "session_id", "type": "STRING"},
    {"name": "driver_number", "type": "STRING"},
    {"name": "abbreviation", "type": "STRING"},
    {"name": "full_name", "type": "STRING"},
    {"name": "team_name", "type": "STRING"},
    {"name": "grid_position", "type": "FLOAT"},
    {"name": "finish_position", "type": "FLOAT"},
    {"name": "points", "type": "FLOAT"},
    {"name": "status", "type": "STRING"},
    {"name": "time", "type": "STRING"},
    {"name": "fastest_lap", "type": "BOOLEAN"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]

RAW_LAPS_SCHEMA = [
    {"name": "session_id", "type": "STRING"},
    {"name": "driver_number", "type": "STRING"},
    {"name": "abbreviation", "type": "STRING"},
    {"name": "lap_number", "type": "INTEGER"},
    {"name": "lap_time_seconds", "type": "FLOAT"},
    {"name": "sector_1_seconds", "type": "FLOAT"},
    {"name": "sector_2_seconds", "type": "FLOAT"},
    {"name": "sector_3_seconds", "type": "FLOAT"},
    {"name": "compound", "type": "STRING"},
    {"name": "tyre_life", "type": "FLOAT"},
    {"name": "is_personal_best", "type": "BOOLEAN"},
    {"name": "pit_in_time_seconds", "type": "FLOAT"},
    {"name": "pit_out_time_seconds", "type": "FLOAT"},
    {"name": "track_status", "type": "STRING"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]

RAW_PIT_STOPS_SCHEMA = [
    {"name": "session_id", "type": "STRING"},
    {"name": "driver_number", "type": "STRING"},
    {"name": "abbreviation", "type": "STRING"},
    {"name": "stop_number", "type": "INTEGER"},
    {"name": "lap_number", "type": "INTEGER"},
    {"name": "pit_duration_seconds", "type": "FLOAT"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]

RAW_WEATHER_SCHEMA = [
    {"name": "session_id", "type": "STRING"},
    {"name": "timestamp", "type": "TIMESTAMP"},
    {"name": "air_temp", "type": "FLOAT"},
    {"name": "track_temp", "type": "FLOAT"},
    {"name": "humidity", "type": "FLOAT"},
    {"name": "rainfall", "type": "BOOLEAN"},
    {"name": "wind_speed", "type": "FLOAT"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]

RAW_DRIVERS_SCHEMA = [
    {"name": "driver_number", "type": "STRING"},
    {"name": "abbreviation", "type": "STRING"},
    {"name": "full_name", "type": "STRING"},
    {"name": "nationality", "type": "STRING"},
    {"name": "team_name", "type": "STRING"},
    {"name": "season", "type": "INTEGER"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]

RAW_CIRCUITS_SCHEMA = [
    {"name": "circuit_key", "type": "STRING"},
    {"name": "circuit_name", "type": "STRING"},
    {"name": "country", "type": "STRING"},
    {"name": "location", "type": "STRING"},
    {"name": "loaded_at", "type": "TIMESTAMP"},
]