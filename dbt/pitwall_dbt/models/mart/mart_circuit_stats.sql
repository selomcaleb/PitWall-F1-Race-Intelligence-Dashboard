with race_results as (
    select * from {{ ref('mart_race_results') }}
),

qualifying as (
    select * from {{ ref('mart_qualifying_results') }}
),

pit_stops as (
    select * from {{ ref('mart_pit_stops') }}
),

-- winner and pole per race
race_summary as (
    select
        r.season,
        r.round_number,
        r.race_name,
        r.country,
        r.location,
        max(case when r.finish_position = 1 then r.abbreviation end) as race_winner,
        max(q.pole_sitter) as pole_sitter
    from race_results r
    left join (
        select season, round_number, abbreviation as pole_sitter
        from qualifying
        where qualifying_position = 1
    ) q
        on r.season = q.season and r.round_number = q.round_number
    group by r.season, r.round_number, r.race_name, r.country, r.location
),

-- average pit stops per race at each circuit
pit_summary as (
    select
        season,
        round_number,
        count(*) / count(distinct abbreviation) as avg_stops_per_driver
    from pit_stops
    group by season, round_number
),

circuit_stats as (
    select
        rs.location,
        rs.country,
        count(distinct concat(rs.season, '_', rs.round_number)) as races_held,
        countif(rs.race_winner = rs.pole_sitter) as pole_to_win_count,
        round(countif(rs.race_winner = rs.pole_sitter) / count(*) * 100, 1) as pole_to_win_pct,
        round(avg(ps.avg_stops_per_driver), 2) as avg_pit_stops_per_driver
    from race_summary rs
    left join pit_summary ps
        on rs.season = ps.season and rs.round_number = ps.round_number
    group by rs.location, rs.country
)

select * from circuit_stats