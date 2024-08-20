import pandas as pd
import boto3
import io
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def postgres_to_minio_etl_parquet_full(table_name: str, bucket_name: str, endpoint_url: str, access_key: str, secret_key: str):
    # Conectar ao cliente S3
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Conectar ao PostgreSQL e extrair todos os dados
    pg_hook = PostgresHook(postgres_conn_id='postgres')
    pg_conn = pg_hook.get_conn()

    try:
        with pg_conn.cursor() as pg_cursor:
            # Obter colunas
            pg_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            columns = [row[0] for row in pg_cursor.fetchall()]
            columns_list_str = ', '.join(columns)

            # Selecionar todos os dados da tabela
            pg_cursor.execute(f"SELECT {columns_list_str} FROM {table_name}")
            rows = pg_cursor.fetchall()

            logger.info(f"Número de registros encontrados: {len(rows)}")

            if rows:
                df = pd.DataFrame(rows, columns=columns)
                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/full_data.parquet", Body=parquet_buffer.getvalue())
                logger.info(f"Dados completos carregados para o S3 no bucket {bucket_name}")

    except Exception as e:
        logger.error(f"Erro ao extrair dados do PostgreSQL: {e}")
    finally:
        pg_conn.close()

    # Conectar ao MariaDB e carregar os dados
    mysql_hook = MySqlHook(mysql_conn_id='mariadb_local')
    connection = mysql_hook.get_conn()

    try:
        with connection.cursor() as cursor:
            # Criar a tabela se não existir
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join([f'{col} VARCHAR(255)' for col in columns])}
            )
            """
            cursor.execute(create_table_sql)
            logger.info(f"Tabela {table_name} verificada/criada no MariaDB")

            # Limpar dados antigos
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            logger.info(f"Tabela {table_name} limpa antes da carga")

            # Inserir dados na tabela
            for index, row in df.iterrows():
                insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(['%s'] * len(columns))})
                """
                cursor.execute(insert_sql, tuple(row))

            connection.commit()
            logger.info(f"Dados completos inseridos na tabela {table_name} no MariaDB")

    except Exception as e:
        logger.error(f"Erro ao conectar ao MariaDB ou inserir dados: {e}")

    finally:
        if connection:
            connection.close()
