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
        l.lap_number,
        l.lap_time_seconds,
        l.compound,
        l.tyre_life,
        l.is_pit_out_lap
    from laps l
    inner join sessions s
        on l.session_id = s.session_id
    where s.session_type = 'R'
      and l.compound is not null
),

-- mark the start of each stint: lap 1, or any pit-out lap
stint_markers as (
    select
        *,
        case
            when lap_number = 1 then 1
            when is_pit_out_lap then 1
            else 0
        end as is_stint_start
    from race_laps
),

-- running sum of stint starts = stint number
with_stint_number as (
    select
        *,
        sum(is_stint_start) over (
            partition by session_id, abbreviation
            order by lap_number
            rows between unbounded preceding and current row
        ) as stint_number
    from stint_markers
),

-- aggregate laps into stints
stints as (
    select
        season,
        round_number,
        race_name,
        session_id,
        abbreviation,
        stint_number,
        min(compound) as compound,
        min(lap_number) as stint_start_lap,
        max(lap_number) as stint_end_lap,
        count(*) as stint_length,
        avg(lap_time_seconds) as avg_lap_time,
        min(lap_time_seconds) as best_lap_time
    from with_stint_number
    group by season, round_number, race_name, session_id, abbreviation, stint_number
)

select * from stints