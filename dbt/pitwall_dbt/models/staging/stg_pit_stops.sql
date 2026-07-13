with source as (
    select * from {{ source('pitwall_raw', 'raw_pit_stops') }}
),

renamed as (
    select
        session_id,
        driver_number,
        abbreviation,
        lap_number,
        stop_number,
        pit_duration_seconds,
        loaded_at

    from source
    where session_id is not null
)

select * from renamed