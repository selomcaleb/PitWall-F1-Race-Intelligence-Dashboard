{{
    config(
        materialized='table',
        partition_by={
            "field": "season",
            "data_type": "int64",
            "range": {
                "start": 2020,
                "end": 2030,
                "interval": 1
            }
        },
        cluster_by=["abbreviation", "round_number"]
    )
}}


with laps as (
    select * from {{ ref('stg_laps') }}
),

sessions as (
    select * from {{ ref('stg_sessions') }}
),

race_laps as (
    select
        s.season,
        s.round_number,
        s.race_name,
        l.session_id,
        l.abbreviation,
        l.driver_number,
        l.lap_number,
        l.lap_time_seconds,
        l.sector_1_seconds,
        l.sector_2_seconds,
        l.sector_3_seconds,
        l.compound,
        l.tyre_life,
        l.is_personal_best,
        l.is_pit_in_lap,
        l.is_pit_out_lap,
        l.is_abnormal_track_status,

        -- a lap is "clean" if it's a normal racing lap
        (
            l.lap_time_seconds is not null
            and not l.is_pit_in_lap
            and not l.is_pit_out_lap
            and not l.is_abnormal_track_status
        ) as is_clean_lap

    from laps l
    inner join sessions s
        on l.session_id = s.session_id
    where s.session_type = 'R'
),

with_driver_stats as (
    select
        *,
        -- how does this lap compare to the driver's median pace in this race
        lap_time_seconds - percentile_cont(lap_time_seconds, 0.5) over (
            partition by session_id, abbreviation
        ) as delta_to_driver_median

    from race_laps
)

select * from with_driver_stats