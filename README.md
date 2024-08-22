# Projeto Engenharia de Dados
## 🚀 Data Pipeline Project

Este repositório contém a estrutura de um projeto completo de pipeline de dados, integrando o Apache Airflow e dbt (Data Build Tool), bem como a utilização de spark na extração dos dados, criação de um storage utilizando o Minio e a utilização dos bancos de dados Postgres e MariaDb. O objetivo deste projeto é fornecer uma base introdutória, porém sólida para a construção, orquestração e transformação de dados, utilizando as melhores práticas do setor, bem como a entrega prática dos meus estudos sobre a área de engenharia de dados. Tive como base de inspiração algumas publicações nessa área, os cursos(links no final) e experiências de trabalho que obtive ao longo dos últimos anos. 
Além dessa parte mais tecnica, deixo aqui uma publicação que fiz, tendo como título "Aspectos essenciais e Práticos sobre Engenharia de Dados"(Link)

Espero que todo esse material possa servir de base para todos aqueles que queiram ingressar ou se aprofundar mais nessa area. 
Bons estudos e bebam água💦!

## 📊 Arquitetura do Pipeline
Abaixo está a representação gráfica da arquitetura deste pipeline de dados:

![Arquitetura do Pipeline](https://github.com/user-attachments/assets/4547f48f-18d5-41e4-8938-c624b6e43a56)

Nesta arquitetura, os dados são extraídos de várias fontes, transformados e carregados em um Data Warehouse utilizando Apache Airflow e dbt, e finalmente consumidos por ferramentas de visualização como o Metabase.

## 📂 Estrutura do Projeto
A estrutura do projeto está organizada da seguinte maneira:

```
/ENG_DADOS_PROJETO1
│
├── .temp/                             # Nessa pasta existe os nossos arquivos iniciais do estudo de extração de dados(Videos no youtube)
│   ├── dag_csv.py
│   └── task_csv.py
│   └── task_parquet_full.py
├── airflow/
│   ├── config_airflow/
│   │   └── airflow.Dockerfile         # Dockerfile customizado para o Airflow
│   │   └── credentials.json           # Credenciais que utilizamos na API do google sheets(por questões de segurança o #github não permite a submissão desse tipo de arquivo)
│   ├── dags/
│   │   └── dag_main.py                # Arquivo principal da DAG contendo as extrações e as transformações em dbt.
│   ├── tasks/
│   │   ├── task_sheets.py             # Arquivo de task contendo a extração dos dados vindos do google sheets
│   │   └── task_parquet.py            # Arquivo de task contendo a extração dos dados vindos do postgres(Projeto feito atraves do curso do Prof. Fernando Amaral)
├── dbt_bike/                          # Nessa pasta existe as transformações de dados vindos do google sheets, aqui utilizamos o BD da empresa "Bikes_Ronaldinho"(nome criado carinhosamente pela minha filha)
│   ├── dbt_project.yml                # Arquivo de configuração principal do dbt
│   ├── profiles.yml                   # Configuração de perfil para conectar ao banco de dados mariadb
│   ├── models/
│   │   ├── dw_dim/
│   │   │   └── dim_cliente_bike.sql   # Modelos de tabelas de dimessão
│   │   │   └── schemas.sql            # Criação do schema de mapeamento das tabelas e colunas que coletamos da nossa camada landing 
│   │   └── dw_fatos/
│   │   │   └── fatos_vendas_bike.sql  # Modelos de tabelas de fatos
│   │   │   └── schemas.sql            # Criação do schema de mapeamento das tabelas e colunas que coletamos da nossa camada landing 
│   ├── dbt_packages/                  # Arquivos de pacotes a serem utilizados pelo proprio dbt         
│   └── seeds/
│       └── seed_data.csv              # Dados de seed para pré-carregar no dbt, utilizados caso fossemos incluir dados vindos em csv(não fizemos isso!)
├── dbt_novadrive_dw/                  # Nessa pasta existe as transformações de dados vindos do postgres, aqui utilizamos o BD da empresa NovaDrive(projeto usado no curso)
│   ├── dbt_project.yml                # Arquivo de configuração principal do dbt
│   ├── profiles.yml                   # Configuração de perfil para conectar ao banco de dados mariadb
│   ├── models/
│   │   ├── dw_dim/
│   │   │   └── dim_clientes.sql       # Modelos de tabelas de dimessão
│   │   │   └── schemas.sql            # Criação do schema de mapeamento das tabelas e colunas que coletamos da nossa camada landing 
│   │   └── dw_fatos/
│   │   │   └── fatos_vendas.sql       # Modelos de tabelas de fatos
│   │   │   └── schemas.sql            # Criação do schema de mapeamento das tabelas e colunas que coletamos da nossa camada landing 
│   ├── dbt_packages/                  # Arquivos de pacotes a serem utilizados pelo proprio dbt         
│   └── seeds/
│       └── seed_data.csv              # Dados de seed para pré-carregar no dbt, utilizados caso fossemos incluir dados vindos em csv(não fizemos isso!)    
├── docker-compose.yaml
├── .gitgnore
├── requirements.txt
├── README.md
```

## 🛠️ Tecnologias Utilizadas 
- **Apache Airflow**: Para orquestração de workflows e automação de tarefas. 
- **dbt (Data Build Tool)**: Para transformação de dados, modelagem e criação de tabelas no data warehouse. 
- **Docker**: Para containerização de serviços, garantindo um ambiente isolado e reprodutível.
- **Spark**: Utilizado para processamento de grandes volumes de dados de maneira distribuída(aqui utilizamos para realizar a extração dos dados). 
- **MariaDB**: Banco de dados utilizado como Data Warehouse para armazenar as tabelas de dimensões e fatos. 
- **Metabase**: Ferramenta de BI para visualização e análise dos dados armazenados no Data Warehouse. 


## 🐳 Docker
O projeto está configurado para rodar em um ambiente Docker. O `docker-compose.yaml` e o `Dockerfile` na raiz do projeto são usados para configurar o ambiente de desenvolvimento e execução dos serviços. Além disso, o Airflow possui um `Dockerfile` customizado para garantir que todas as dependências específicas sejam atendidas.

## 📄 Airflow
- **DAGs**: As DAGs (Directed Acyclic Graphs) são definidas dentro da pasta `airflow/dags/`. O arquivo principal é o `dag_main.py`, que orquestra as diferentes tarefas.
- **Tasks**: As tarefas são modularizadas dentro da pasta `airflow/tasks/`. Um exemplo é o `task_parquet.py`, que pode conter lógica para processar arquivos parquet.
- **Configurações**: Todas as configurações e customizações específicas do Airflow estão na pasta `airflow/config_airflow/`.

## 🏗️ dbt
- **Configuração**: O arquivo `dbt_project.yml` contém as configurações principais do dbt, enquanto o `profiles.yml` é usado para definir os perfis de conexão com os bancos de dados.
- **Modelos**: Os modelos de dados são organizados em pastas como `dim_tables`, e `fatos_tables`. Esses arquivos SQL definem as tabelas e vistas no data warehouse.
- **Macros**: Funções personalizadas que podem ser usadas nos modelos dbt estão em `macros/custom_macros.sql`.

## 🚀 Como Começar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/eng_dados_projeto1.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd eng_dados_projeto1
   ```
3. Suba os containers com Docker:
   ```bash
   docker-compose up -d
   ```
4. Acesse o Airflow na URL `http://localhost:8080` e inicie as DAGs conforme necessário.

## 📚 Documentação

- [Documentação Oficial do Airflow](https://airflow.apache.org/docs/)
- [Documentação Oficial do dbt](https://docs.getdbt.com/)
- [Documentação Oficial do Docker](https://docs.docker.com)
- [Documentação Oficial do Metabase](https://www.metabase.com/docs/latest/)

## 📋 Contribuições e Duvidas

Contribuições e duvidas são bem-vindas, qualquer coisa manda msg!

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
