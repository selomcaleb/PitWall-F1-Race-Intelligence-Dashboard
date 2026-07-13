with results as (
    select * from {{ ref('stg_results') }}
),

sessions as (
    select * from {{ ref('stg_sessions') }}
),

race_results as (
    select
        s.season,
        s.round_number,
        s.race_name,
        s.country,
        s.location,
        s.session_date,
        r.session_id,
        r.driver_number,
        r.abbreviation,
        r.full_name,
        r.team_name,
        r.grid_position,
        r.finish_position,
        r.positions_gained,
        r.points,
        r.status,
        r.finish_time,
        r.is_classified,

        -- flag DNFs
        case
            when r.is_classified = false then true
            else false
        end as is_dnf

    from results r
    inner join sessions s
        on r.session_id = s.session_id
    where s.session_type = 'R'
)

select * from race_results