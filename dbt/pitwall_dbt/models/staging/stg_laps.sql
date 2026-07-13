with source as (
    select * from {{ source('pitwall_raw', 'raw_laps') }}
),

renamed as (
    select
        session_id,
        driver_number,
        abbreviation,
        lap_number,
        lap_time_seconds,
        sector_1_seconds,
        sector_2_seconds,
        sector_3_seconds,
        upper(compound) as compound,
        cast(tyre_life as int64) as tyre_life,
        is_personal_best,
        pit_in_time_seconds,
        pit_out_time_seconds,
        track_status,
        loaded_at,

        -- derived columns
        pit_in_time_seconds is not null as is_pit_in_lap,
        pit_out_time_seconds is not null as is_pit_out_lap,
        track_status != '1' as is_abnormal_track_status

    from source
    where session_id is not null
      and lap_number is not null
)

select * from renamed