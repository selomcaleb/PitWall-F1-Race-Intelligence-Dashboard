with results as (
    select * from {{ ref('stg_results') }}
),

sessions as (
    select * from {{ ref('stg_sessions') }}
),

quali as (
    select
        s.season,
        s.round_number,
        s.race_name,
        s.session_date,
        r.session_id,
        r.abbreviation,
        r.full_name,
        r.team_name,
        r.finish_position as qualifying_position
    from results r
    inner join sessions s
        on r.session_id = s.session_id
    where s.session_type = 'Q'
)

select * from quali