with source_data as (
    select 
        VendasID,
        VendedorID as codigo_vendedor,
        ClienteID as codigo_cliente,
        Data as data_venda,
        Total as valor_total
    from {{ source('lakeestudo', 'Vendas_Bike') }}
)
select *
from source_data
