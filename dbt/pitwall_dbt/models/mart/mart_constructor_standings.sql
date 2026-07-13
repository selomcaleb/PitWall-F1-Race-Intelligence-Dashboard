with race_results as (
    select * from {{ ref('mart_race_results') }}
),

points_per_round as (
    select
        season,
        round_number,
        race_name,
        session_date,
        team_name,
        sum(coalesce(points, 0)) as team_points
    from race_results
    group by season, round_number, race_name, session_date, team_name
),

cumulative as (
    select
        *,
        sum(team_points) over (
            partition by season, team_name
            order by round_number
            rows between unbounded preceding and current row
        ) as cumulative_points
    from points_per_round
),

with_position as (
    select
        *,
        rank() over (
            partition by season, round_number
            order by cumulative_points desc
        ) as constructor_position
    from cumulative
)

select * from with_position