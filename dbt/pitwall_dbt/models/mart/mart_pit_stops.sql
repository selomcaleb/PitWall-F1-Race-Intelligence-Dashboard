with pit_stops as (
    select * from {{ ref('stg_pit_stops') }}
),

sessions as (
    select * from {{ ref('stg_sessions') }}
),

laps as (
    select * from {{ ref('stg_laps') }}
)

select
    s.season,
    s.round_number,
    s.race_name,
    p.session_id,
    p.abbreviation,
    p.driver_number,
    p.stop_number,
    p.lap_number,
    p.pit_duration_seconds,
    l.compound as compound_after_stop,
    l.tyre_life as tyre_age_after_stop

from pit_stops p
inner join sessions s
    on p.session_id = s.session_id
left join laps l
    on p.session_id = l.session_id
    and p.abbreviation = l.abbreviation
    and p.lap_number + 1 = l.lap_number
where s.session_type = 'R'