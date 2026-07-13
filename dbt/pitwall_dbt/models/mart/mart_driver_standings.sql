with race_results as (
    select * from {{ ref('mart_race_results') }}
),

points_per_round as (
    select
        season,
        round_number,
        race_name,
        session_date,
        abbreviation,
        full_name,
        team_name,
        coalesce(points, 0) as points
    from race_results
),

cumulative as (
    select
        season,
        round_number,
        race_name,
        session_date,
        abbreviation,
        full_name,
        team_name,
        points as round_points,

        -- running total of points across the season
        sum(points) over (
            partition by season, abbreviation
            order by round_number
            rows between unbounded preceding and current row
        ) as cumulative_points

    from points_per_round
),

with_position as (
    select
        *,
        -- championship position after each round
        rank() over (
            partition by season, round_number
            order by cumulative_points desc
        ) as championship_position

    from cumulative
)

select * from with_position