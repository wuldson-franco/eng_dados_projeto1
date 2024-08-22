with source_data as (
    select * 
    from {{ source('lakeestudo', 'Clientes_Bike') }}
)
select *
from source_data
