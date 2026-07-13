with standings as (
    select * from {{ ref('mart_driver_standings') }}
),

latest_per_driver as (
    select
        season,
        abbreviation,
        full_name,
        team_name,
        cumulative_points as final_points,
        round_number as last_round_raced,
        row_number() over (
            partition by season, abbreviation
            order by round_number desc
        ) as rn
    from standings
),

final as (
    select
        season,
        abbreviation,
        full_name,
        team_name,
        final_points,
        last_round_raced,
        rank() over (
            partition by season
            order by final_points desc
        ) as final_championship_position
    from latest_per_driver
    where rn = 1
)

select * from final