with sessions as (
    select * from {{ ref('stg_sessions') }}
),

races as (
    select
        season,
        round_number,
        race_name,
        country,
        location,
        circuit_key,
        session_date as race_date
    from sessions
    where session_type = 'R'
)

select
    *,
    case
        when race_date < current_date() then 'completed'
        else 'upcoming'
    end as race_status
from races
order by season, round_number