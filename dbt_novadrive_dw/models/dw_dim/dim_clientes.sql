with source_data as (
    select *
    from {{ source('lakeestudo', 'clientes')}}
)
select * 
from source_data