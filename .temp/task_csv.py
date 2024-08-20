#SALVANDO EM CSV

import pandas as pd
import boto3
from airflow.providers.postgres.hooks.postgres import PostgresHook

def postgres_to_minio_etl_csv(table_name: str, bucket_name: str, endpoint_url: str, access_key: str, secret_key: str):
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=f"{table_name}/max_id.txt")
        max_id = int(obj['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        max_id = 0

    with PostgresHook(postgres_conn_id='postgres').get_conn() as pg_conn:
        with pg_conn.cursor() as pg_cursor:
            primary_key = f'id_{table_name}'

            pg_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            columns = [row[0] for row in pg_cursor.fetchall()]
            columns_list_str = ', '.join(columns)

            pg_cursor.execute(f"SELECT {columns_list_str} FROM {table_name} WHERE {primary_key} > %s", (max_id,))
            rows = pg_cursor.fetchall()

            if rows:
                df = pd.DataFrame(rows, columns=columns)
                csv_buffer = df.to_csv(index=False)
                s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/data_{max_id + 1}.csv", Body=csv_buffer)
                max_id = df[primary_key].max()
                s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/max_id.txt", Body=str(max_id))
