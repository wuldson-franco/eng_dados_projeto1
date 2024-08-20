import pandas as pd
import boto3
import io
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def postgres_to_minio_etl_parquet(table_name: str, bucket_name: str, endpoint_url: str, access_key: str, secret_key: str):
    # Conectar ao cliente S3
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Etapa de leitura e escrita no S3
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=f"{table_name}/max_id.txt")
        max_id = int(obj['Body'].read().decode('utf-8'))
        logger.info(f"Max ID encontrado no S3: {max_id}")
    except s3_client.exceptions.NoSuchKey:
        max_id = 0
        logger.info("Nenhum max_id encontrado no S3, iniciando com max_id = 0")

    # Conectar ao PostgreSQL e extrair dados
    pg_hook = PostgresHook(postgres_conn_id='postgres')
    pg_conn = pg_hook.get_conn()
    df = None

    try:
        with pg_conn.cursor() as pg_cursor:
            primary_key = f'id_{table_name}'

            # Obter colunas e dados
            pg_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            columns = [row[0] for row in pg_cursor.fetchall()]
            columns_list_str = ', '.join(columns)

            pg_cursor.execute(f"SELECT {columns_list_str} FROM {table_name} WHERE {primary_key} > %s", (max_id,))
            rows = pg_cursor.fetchall()

            if rows:
                df = pd.DataFrame(rows, columns=columns)
                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/data_{max_id + 1}.parquet", Body=parquet_buffer.getvalue())
                max_id = df[primary_key].max()
                s3_client.put_object(Bucket=bucket_name, Key=f"{table_name}/max_id.txt", Body=str(max_id))
                logger.info(f"Dados carregados e max_id atualizado para {max_id}")

    except Exception as e:
        logger.error(f"Erro ao extrair dados do PostgreSQL: {e}")
    finally:
        pg_conn.close()

    if df is not None:
        # Conectar ao MariaDB e escrever os dados
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

                # Inserir ou atualizar dados na tabela
                for index, row in df.iterrows():
                    # Atualizar dados se já existir
                    update_sql = f"""
                    UPDATE {table_name}
                    SET {', '.join([f'{col} = %s' for col in columns])}
                    WHERE {primary_key} = %s
                    """
                    cursor.execute(update_sql, tuple(row.tolist()) + (row[primary_key],))

                    # Inserir novos dados se não existir
                    insert_sql = f"""
                    INSERT IGNORE INTO {table_name} ({', '.join(columns)})
                    VALUES ({', '.join(['%s'] * len(columns))})
                    """
                    cursor.execute(insert_sql, tuple(row))

                connection.commit()
                logger.info(f"Dados inseridos/atualizados na tabela {table_name} no MariaDB")

        except Exception as e:
            logger.error(f"Erro ao conectar ao MariaDB ou inserir dados: {e}")

        finally:
            if connection:
                connection.close()
    else:
        logger.info("Nenhum dado para processar.")
