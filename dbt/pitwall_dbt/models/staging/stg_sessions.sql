with source as (
    select * from {{ source('pitwall_raw', 'raw_sessions') }}
),

renamed as (
    select
        session_id,
        season,
        round_number,
        country,
        location,
        circuit_key,
        session_type,
        session_date,
        loaded_at,

        -- derived columns
        case
            when session_type = 'R' then 'Race'
            when session_type = 'Q' then 'Qualifying'
            else session_type
        end as session_type_name,

        concat(cast(season as string), ' ', country, ' Grand Prix') as race_name

    from source
    where session_id is not null
)

select * from renamed