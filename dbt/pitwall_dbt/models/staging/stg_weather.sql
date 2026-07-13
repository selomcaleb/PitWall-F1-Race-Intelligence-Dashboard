with source as (
    select * from {{ source('pitwall_raw', 'raw_weather') }}
),

renamed as (
    select
        session_id,
        timestamp as reading_time,
        air_temp,
        track_temp,
        humidity,
        rainfall,
        wind_speed,
        loaded_at

    from source
    where session_id is not null
)

select * from renamed