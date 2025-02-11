import os
import pandas as pd
import unicodedata
from sqlalchemy import create_engine, text

# Function to clean column names for PostgreSQL compatibility
def clean_column_names(columns):
    """Normalize column names: remove accents, lowercase, and replace spaces/special chars with underscores."""
    cleaned_columns = [
        "".join(c if c.isalnum() or c == "_" else ""
                for c in unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8').lower().replace(" ", "_").replace("-", "_"))
        for col in columns
    ]
    return cleaned_columns

# Helper function to read and clean Excel data
def read_and_clean_excel(file_path, sheet_name=0, skiprows=None):
    """Reads an Excel file, cleans the column names, and returns a DataFrame."""
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)
    df.columns = clean_column_names(df.columns)
    return df

# Function to import a specific Excel file into the database
def import_excel_file(file_path, table_name, engine, sheet_name=0, skiprows=None):
    """
    Imports an Excel file into a PostgreSQL database.

    Parameters:
        file_path (str): Path to the Excel file.
        table_name (str): Target table name in the database.
        engine (SQLAlchemy Engine): Database connection engine.
        sheet_name (int): Sheet to read from Excel file.
        skiprows (int): Number of rows to skip at the start of the file.
        numeric_columns (list): List of numeric columns to convert.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}. Check the file path.")
        return

    print(f"Processing Excel file: {file_path}")
    try:
        # Read and clean the Excel data
        df = read_and_clean_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)


        # Write the DataFrame to the database
        df.to_sql(
            name=table_name,
            con=engine,
            schema="imp",
            if_exists="append",
            index=False
        )
        print(f"Data from '{file_path}' imported successfully into table '{table_name}'.")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# PostgreSQL connection details
db_user = "postgres"
db_password = "123456"
db_host = "localhost"  # Change if needed
db_port = "5431"
db_name = "enem"

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

with engine.connect() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS imp;"))

# Path to the target file
target_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/notas_de_corte/2019_2024/vagas_ofertadas_por_semestre/relatorio_oferta_sisu_2024_vagas_1_e_2_semestre.xlsx"))

# Define table name based on the file name
table_name = "sisu_offer_report"

# Import the file
import_excel_file(
    file_path=target_file,
    table_name=table_name,
    engine=engine,
    sheet_name=1,  # Adjust if the data is on a different sheet
    skiprows=0    # Adjust if rows need to be skipped
)