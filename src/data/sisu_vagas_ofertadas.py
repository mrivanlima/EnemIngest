import pandas as pd
from sqlalchemy import create_engine, text

# Step 1: Read the Excel file into a DataFrame
# Path to the Excel file
excel_file_path = "../../data/Portal_Sisu 2024_Vagas ofertadas.xlsx"

df = pd.read_excel(excel_file_path, sheet_name="adesao_2024")

# Clean column names for PostgreSQL compatibility
df.columns = df.columns.str.replace(' ', '_').str.lower()

# Optional: Display the first few rows
print(df.head())

# Step 2: Establish a connection to PostgreSQL
db_user = "postgres"
db_password = "123456"
db_host = "localhost"  # or your host address
db_port = "5431"
db_name = "enem"

# Create the connection engine
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Step 3: Ensure the schema exists
with engine.connect() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS app;"))

# Step 4: Write the DataFrame to the PostgreSQL table in the 'app' schema
table_name = "sisu_vagas_ofertadas"

df.to_sql(
    name=table_name,
    con=engine,
    schema="app",          # Specify the schema explicitly
    if_exists="replace",   # Replace the table if it exists
    index=False            # Don't write the DataFrame index as a column
)

print(f"Table '{table_name}' has been successfully created in the 'app' schema of the database '{db_name}'.")
