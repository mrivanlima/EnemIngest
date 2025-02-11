import os
import pandas as pd
import unicodedata
from sqlalchemy import create_engine, text

# Function to clean column names for PostgreSQL compatibility
def clean_column_names(columns):
    """Normalize column names: remove accents, lowercase, and replace spaces/special chars with underscores."""
    cleaned_columns = []
    for col in columns:
        # Normalize Unicode (remove accents like é, ç, ã)
        col = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8')
        # Convert to lowercase
        col = col.lower()
        # Replace spaces and special characters with underscores
        col = col.replace(" ", "_").replace("-", "_")
        # Remove any remaining non-alphanumeric characters (except underscores)
        col = "".join(c if c.isalnum() or c == "_" else "" for c in col)
        cleaned_columns.append(col)
    return cleaned_columns

# Function to import files into the db
def import_excel_2010_2018(target_dir, table_name, engine):
    """
    Imports a single Excel file (2010-2018 SISU data) into a PostgreSQL database.
    
    Parameters:
        target_dir (str): Directory containing the Excel file.
        table_name (str): Target table name in the database.
        engine (SQLAlchemy Engine): Database connection engine.
    """
    # Ensure the file has the correct extension
    item_path = os.path.join(target_dir, "PORTAL_Sisu 2010 a 2018_Nota de corte.xlsx")  # Ensure correct extension
    print(f"Processing Excel file: {item_path}")
    
    try:
        # Read Excel file, skipping first 4 rows (header is on row 5)
        df = pd.read_excel(item_path, skiprows=4)

        # Ensure column names are properly cleaned
        if "clean_column_names" in globals():
            df.columns = clean_column_names(df.columns)  # If you have a function to clean column names
        else:
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]  # Basic cleaning

        numeric_columns = ['percentual_de_bonus', 'nota_de_corte']  # Replace with actual column names
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert invalid values to NaN

        # Write the DataFrame to the database
        df.to_sql(
            name=table_name,
            con=engine,
            schema="imp",
            if_exists="append",  # Change to "replace" if structure mismatch
            index=False
        )
        print(f"Data from '{item_path}' imported successfully into table '{table_name}'.")
    
    except FileNotFoundError:
        print(f"Error: File not found at {item_path}. Check the file path.")
    
    except Exception as e:
        print(f"Error processing {item_path}: {e}")

# Function to import files into the db
def import_excel_dictionary(target_dir, table_name, engine):
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isfile(item_path) and item.endswith('.xlsx'):
            print(f"Processing Excel file in main directory: {item_path}")
            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(item_path, sheet_name=0)

                # Clean column names
                df.columns = clean_column_names(df.columns)

                # Write the DataFrame to the database
                df.to_sql(
                    name=table_name,
                    con=engine,
                    schema="imp",
                    if_exists="append",
                    index=False
                )
                print(f"Table '{table_name}' created successfully in schema 'imp'.")
            except Exception as e:
                print(f"Error processing {item_path}: {e}")
        

# Function to import files into the db
def import_excel_2019_2024(target_dir, table_name, engine):
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isfile(item_path) and item.endswith('.xlsx'):
            print(f"Processing Excel file in main directory: {item_path}")
            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(item_path, sheet_name=1)

                # Clean column names
                df.columns = clean_column_names(df.columns)

                # Write the DataFrame to the database
                df.to_sql(
                    name=table_name,
                    con=engine,
                    schema="imp",
                    if_exists="append",
                    index=False
                )
                print(f"Table '{table_name}' created successfully in schema 'imp'.")
            except Exception as e:
                print(f"Error processing {item_path}: {e}")

# print(os.listdir(target_dir))

# PostgreSQL connection details
db_user = "postgres"
db_password = "123456"
db_host = "localhost"  # Change if needed
db_port = "5431"
db_name = "enem"

# Create the connection engine
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Ensure the schema exists
with engine.connect() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS imp;"))

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/notas_de_corte/2010_2018"))

# print(os.listdir(target_dir))

# Define table name based on the file name
table_name = "enem_cutoff_scores_2010_2018"

import_excel_2010_2018(target_dir, table_name, engine)


target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/notas_de_corte/2019_2024"))

# Define table name based on the file name
table_name = "enem_dictionary"

import_excel_dictionary(target_dir, table_name, engine)

# Define table name based on the file name
table_name = "enem_cutoff_scores_2019_2024"

import_excel_2019_2024(target_dir, table_name, engine)
