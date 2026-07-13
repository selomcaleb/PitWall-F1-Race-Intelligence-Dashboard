with source as (
    select * from {{ source('pitwall_raw', 'raw_circuits') }}
),

deduped as (
    select
        circuit_key,
        circuit_name,
        country,
        location,
        loaded_at,
        row_number() over (
            partition by circuit_key
            order by loaded_at desc
        ) as row_num
    from source
    where circuit_key is not null
)

select
    circuit_key,
    circuit_name,
    country,
    location,
    loaded_at
from deduped
where row_num = 1