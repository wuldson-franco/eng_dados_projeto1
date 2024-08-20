#SALVANDO EM CSV

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
import boto3
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}

@dag(
    dag_id='postgres_to_minio_csv',
    default_args=default_args,
    description='Carga Incremental do Postgres to MinIO em csv',
    schedule_interval=timedelta(days=1),
    catchup=False
)
def postgres_to_minio_etl():
    table_names = ['veiculos', 'estados', 'cidades', 'concessionarias', 'vendedores', 'clientes', 'vendas']

    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',  # Altere para o endpoint do seu MinIO
        aws_access_key_id='minioadmin',    # Altere para sua chave de acesso
        aws_secret_access_key='minio@1234!' # Altere para sua chave secreta
    )
    bucket_name = 'landing' # Altere para o nome do seu bucket

    for table_name in table_names:
        @task(task_id=f'get_max_id_{table_name}')
        def get_max_primary_key(table_name: str):
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=f"{table_name}/max_id.txt")
                max_id = int(response['Body'].read().decode('utf-8'))
            except s3_client.exceptions.NoSuchKey:
                max_id = 0
            return max_id

        @task(task_id=f'load_data_{table_name}')
        def load_incremental_data(table_name: str, max_id: int):
            with PostgresHook(postgres_conn_id='postgres').get_conn() as pg_conn:
                with pg_conn.cursor() as pg_cursor:
                    primary_key = f'id_{table_name}'

                    pg_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
                    columns = [row[0] for row in pg_cursor.fetchall()]
                    columns_list_str = ', '.join(columns)

                    pg_cursor.execute(f"SELECT {columns_list_str} FROM {table_name} WHERE {primary_key} > {max_id}")
                    rows = pg_cursor.fetchall()

                    if rows:
                        df = pd.DataFrame(rows, columns=columns)
                        csv_buffer = df.to_csv(index=False)
                        s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/data_{max_id + 1}.csv", Body=csv_buffer)
                        max_id = df[primary_key].max()
                        s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/max_id.txt", Body=str(max_id))

        max_id = get_max_primary_key(table_name)
        load_incremental_data(table_name, max_id)

postgres_to_minio_etl_dag = postgres_to_minio_etl()
