import os
import pandas as pd
import unicodedata
from sqlalchemy import create_engine, text
import gc  # Importa o garbage collector

# Função de limpeza dos nomes das colunas
def clean_column_names(columns):
    cleaned_columns = []
    for col in columns:
        col = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8')
        col = col.lower().replace(" ", "_").replace("-", "_")
        col = "".join(c if c.isalnum() or c == "_" else "" for c in col)
        cleaned_columns.append(col)
    return cleaned_columns

# Função para importar arquivos de Excel (2010-2018)
def import_excel_2010_2018(target_dir, table_name, engine):
    item_path = os.path.join(target_dir, "PORTAL_Sisu 2010 a 2018_Vagas ofertadas.xlsx")
    print(f"Processing Excel file: {item_path}")

    try:
        df = pd.read_excel(item_path, skiprows=4)
        df.columns = clean_column_names(df.columns)

        print(df.head())

        numeric_columns = ['cod_ies', 'cod_curso', 'percentual_de_bonus', 'qt_vagas']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.to_sql(
            name=table_name,
            con=engine,
            schema="imp",
            if_exists="replace",
            index=False
        )

        print(f"Data from '{item_path}' imported successfully into table '{table_name}'.")

    except FileNotFoundError:
        print(f"Error: File not found at {item_path}. Check the file path.")
    
    except Exception as e:
        print(f"Error processing {item_path}: {e}")
    
    finally:
        # Libera memória após o processamento
        del df
        gc.collect()

# Função para importar arquivos Excel (2019-2025)
def import_excel_2019_2025(target_dir, table_name, engine):
    dataframes = []  # Lista para armazenar os DataFrames temporariamente

    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isfile(item_path) and item.endswith('.xlsx'):
            print(f"Processing Excel file: {item_path}")

            try:
                # Carrega os dados de cada arquivo
                df = pd.read_excel(item_path, sheet_name=1)
                df.columns = clean_column_names(df.columns)

                if 'edicao' in df.columns:
                    df.rename(columns={'edicao': 'nu_ano'}, inplace=True)

                # Remove a coluna `edicao` caso ainda esteja presente
                if 'edicao' in df.columns:
                    df.drop(columns=['edicao'], inplace=True)

                # Adiciona o DataFrame à lista
                dataframes.append(df)

                print(f"File '{item_path}' loaded successfully.")
            
            except Exception as e:
                print(f"Error processing {item_path}: {e}")
            
            finally:
                del df
                gc.collect()

    # Concatenar todos os DataFrames em um único DataFrame
    if dataframes:
        final_df = pd.concat(dataframes, ignore_index=True)
        
        # Insere os dados no banco de uma vez só
        final_df.to_sql(
            name=table_name,
            con=engine,
            schema="imp",
            if_exists="replace",  # Pode mudar para 'append' se necessário
            index=False
        )
        print(f"All data successfully imported into table '{table_name}'.")


# Configurações de conexão
db_user = "postgres"
db_password = "123456"
db_host = "localhost"
db_port = "5431"
db_name = "enem"

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Garante que o schema existe
with engine.connect() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS imp;"))

# Importação dos arquivos
target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/vagas_ofertadas/2010_2018"))
table_name = "enem_vagas_ofertadas_2010_2018"
import_excel_2010_2018(target_dir, table_name, engine)

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/vagas_ofertadas/2019_2025"))

table_name = "enem_vagas_ofertadas_2019_2025"
import_excel_2019_2025(target_dir, table_name, engine)
