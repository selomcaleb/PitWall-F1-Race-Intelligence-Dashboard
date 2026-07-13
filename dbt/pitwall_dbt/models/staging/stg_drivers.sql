with source as (
    select * from {{ source('pitwall_raw', 'raw_drivers') }}
),

deduped as (
    select
        driver_number,
        abbreviation,
        full_name,
        team_name,
        nationality,
        season,
        loaded_at,
        row_number() over (
            partition by abbreviation, season
            order by loaded_at desc
        ) as row_num
    from source
    where abbreviation is not null
)

select
    driver_number,
    abbreviation,
    full_name,
    team_name,
    nationality,
    season,
    loaded_at
from deduped
where row_num = 1