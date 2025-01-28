import os
import pandas as pd
from sqlalchemy import create_engine, text

# Get the absolute path of the target directory
script_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(script_dir, "..", "..", "data", "notas_de_corte")

# Debugging: Print the resolved target directory
print(f"Resolved target_dir: {target_dir}")

if not os.path.exists(target_dir):
    raise FileNotFoundError(f"Directory {target_dir} does not exist!")

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

# Function to clean column names for PostgreSQL compatibility
def clean_column_names(columns):
    return columns.str.replace(' ', '_').str.replace('.', '_').str.lower()

# Step 1: Check for .xlsx files in target_dir directly
for item in os.listdir(target_dir):
    item_path = os.path.join(target_dir, item)

    # If the item is a file and ends with .xlsx, process it
    if os.path.isfile(item_path) and item.endswith('.xlsx'):
        print(f"Processing Excel file in main directory: {item_path}")
        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(item_path, sheet_name=1)  # Adjust sheet_name if needed

            # Clean column names
            df.columns = clean_column_names(df.columns)

            # Define table name based on the file name
            table_name = os.path.splitext(item)[0].replace(' ', '_').lower()

            # Write the DataFrame to the database
            df.to_sql(
                name=table_name,
                con=engine,
                schema="imp",
                if_exists="replace",  # Replace the table if it exists
                index=False  # Don't include the DataFrame index as a column
            )
            print(f"Table '{table_name}' created successfully in schema 'imp'.")
        except Exception as e:
            print(f"Error processing {item_path}: {e}")
