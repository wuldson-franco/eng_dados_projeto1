from datetime import timedelta
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup

from tasks.task_parquet import postgres_to_minio_etl_parquet
from tasks.task_sheets import google_sheet_to_minio_etl
#from tasks.task_parquet_full import postgres_to_minio_etl_parquet_full

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='main_dag',
    default_args=default_args,
    description='Main DAG calling different tasks',
    schedule_interval=timedelta(days=1),
    catchup=False
)
def main_dag():
    table_names = ['veiculos', 'estados', 'cidades', 'concessionarias', 'vendedores', 'clientes', 'vendas']  # Altere conforme necessário
    google_sheets = ['Clientes_Bike', 'Vendedores_Bike', 'Produtos_Bike', 'Vendas_Bike', 'ItensVendas_Bike']  # Altere para o nome das abas da sua planilha
    bucket_name = 'landing'
    endpoint_url = 'http://minio:9000'
    access_key = 'minioadmin'
    secret_key = 'minio@1234!'
    sheet_id = '1feUG0eV9ekpwsW9CFa4EophJDUvbBaNoSPdm13mWnoo'


    #with TaskGroup("group_task_parquet_full", tooltip="Tasks processadas do BD externo para minio, salvando em .parquet") as group_task_parquet_full:
    #    for table_name in table_names:
    #        PythonOperator(
    #            task_id=f'task_parquet_full_{table_name}',
    #            python_callable=postgres_to_minio_etl_parquet_full,
    #            op_args=[table_name, bucket_name, endpoint_url, access_key, secret_key]
    #        )

    with TaskGroup("group_task_parquet", tooltip="Tasks processadas do BD externo para minio, salvando em .parquet") as group_task_parquet:
        for table_name in table_names:
            PythonOperator(
                task_id=f'task_parquet_{table_name}',
                python_callable=postgres_to_minio_etl_parquet,
                op_args=[table_name, bucket_name, endpoint_url, access_key, secret_key]
            )

    with TaskGroup("group_task_sheets", tooltip="Tasks processadas do google sheets para minio, salvando em .parquet") as group_task_sheets:
        for sheets_name in google_sheets:
            PythonOperator(
                task_id=f'task_sheets_{sheets_name}',
                python_callable=google_sheet_to_minio_etl,
                op_args=[sheet_id, sheets_name, bucket_name, endpoint_url, access_key, secret_key]
            )

    # Definindo a ordem de execução dos grupos
    #group_task_parquet_full >> 
    group_task_parquet >> group_task_sheets

main_dag_instance = main_dag()
