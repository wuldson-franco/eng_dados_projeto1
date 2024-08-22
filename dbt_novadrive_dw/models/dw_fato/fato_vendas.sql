with source_data as (
    select 
        id_vendas as cod_vendas,
        id_veiculos as cod_veiculo,
        id_concessionarias as cod_concessionaria,
        id_vendedores as cod_vendedores,
        valor_pago,
        data_venda,
        data_inclusao as data_cadastro
    from {{ source('lakeestudo', 'vendas')}}
)
select * 
from source_data