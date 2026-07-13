with source as (
    select * from {{ source('pitwall_raw', 'raw_results') }}
),

deduped as (
    select
        *,
        row_number() over (
            partition by session_id, driver_number
            order by loaded_at desc
        ) as row_num
    from source
    where session_id is not null
),

renamed as (
    select
        session_id,
        driver_number,
        abbreviation,
        full_name,
        team_name,
        cast(grid_position as int64) as grid_position,
        cast(finish_position as int64) as finish_position,
        points,
        status,
        time as finish_time,
        loaded_at,

        cast(grid_position as int64) - cast(finish_position as int64) as positions_gained,
        case
            when status = 'Finished' then true
            when status like '+%' then true
            else false
        end as is_classified

    from deduped
    where row_num = 1
)

select * from renamed