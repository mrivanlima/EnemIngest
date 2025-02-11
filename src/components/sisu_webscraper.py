import os
from pydantic import BaseModel, HttpUrl
from rich import print
from curl_cffi import requests
from typing import List, Optional
import pandas as pd
import unicodedata
from sqlalchemy import create_engine, text





CSV_SAVE_DIRECTORY = "../../data"




class Institution(BaseModel):
    co_ies: str
    no_ies: str
    sg_ies: str
    sg_uf: str
    co_municipio: str
    no_municipio: str
    no_sitio_ies: str

class FileRecord(BaseModel):
    co_arquivo: str
    co_edicao: str
    co_ies: str
    no_arquivo: str
    ds_caminho_arquivo: HttpUrl
    tp_arquivo: str
    dt_inclusao: str
    dt_alteracao: Optional[str]
    st_ativo: str





def new_session() -> requests.Session:
    """Create a new HTTP session."""
    session = requests.Session(impersonate="chrome", proxy=os.getenv("stickyproxy"))
    return session


def search_api(session: requests.Session) -> List[Institution]:
    """Fetch and parse institutions from the API."""
    url = "https://sisu-api.sisu.mec.gov.br/api/v1/oferta/instituicoes"
    resp = session.get(url)
    resp.raise_for_status()
    institutions = [Institution(**item) for item in resp.json()]
    return institutions


def search_csv(session: requests.Session, item: Institution) -> Optional[FileRecord]:
    """Fetch a CSV record for a given institution."""
    url = f"https://sisu-api.sisu.mec.gov.br/api/v1/arquivo/{item.co_ies}/chamada_regular"
    resp = session.get(url)

    if resp.status_code == 404:
        print(f"[yellow]No CSV found for Institution {item.co_ies}[/yellow]")
        return None

    resp.raise_for_status()

    records = [FileRecord(**record) for record in resp.json()]
    return records[0] if records else None


def download_and_save_csv(session: requests.Session, file_record: FileRecord, save_directory: str = "data/mec_chamada_regular"):
    """Download and save CSV content to a specified directory."""
    url = str(file_record.ds_caminho_arquivo)
    resp = session.get(url)
    resp.raise_for_status()

    safe_filename = file_record.no_arquivo.replace("/", "_")
    file_name = f"{file_record.co_ies}_{safe_filename}.csv"
    file_path = os.path.join(save_directory, file_name)

    print(f"[cyan]Downloading CSV file: {file_path} from {url}[/cyan]")

    os.makedirs(save_directory, exist_ok=True)

    with open(file_path, "wb") as file:
        file.write(resp.content)

    print(f"[green]CSV saved to {file_path}[/green]")
    return file_path





def clean_column_names(columns):
    """Normalize column names: remove accents, lowercase, and replace spaces/special chars with underscores."""
    cleaned_columns = [
        "".join(c if c.isalnum() or c == "_" else ""
                for c in unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('utf-8').lower().replace(" ", "_").replace("-", "_"))
        for col in columns
    ]
    return cleaned_columns


# Helper function to read and clean CSV data
def read_and_clean_csv(file_path, delimiter=";", skiprows=None):
    """
    Reads a CSV file with a specific delimiter, cleans the column names, and returns a DataFrame.
    
    Parameters:
        file_path (str): Path to the CSV file.
        delimiter (str): CSV delimiter (default is ';' for semicolon).
        skiprows (int, optional): Number of rows to skip at the start of the file.
    
    Returns:
        DataFrame: Cleaned Pandas DataFrame.
    """
    df = pd.read_csv(file_path, delimiter=delimiter, skiprows=skiprows)
    
    df.columns = clean_column_names(df.columns)
    
    return df


def import_csv_file(file_path, table_name, engine, delimiter=";", skiprows=None):
    """
    Imports a CSV file into a PostgreSQL database.
    Ensures that column names match before inserting data.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}. Check the file path.")
        return

    print(f"Processing CSV file: {file_path}")
    try:
        df = read_and_clean_csv(file_path, delimiter=delimiter, skiprows=skiprows)

        # print("[cyan]First few rows of CSV data:[/cyan]")
        # print(df.head())
        # print(f"[yellow]CSV Columns: {df.columns.tolist()}[/yellow]")

        with engine.connect() as connection:
            result = connection.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'imp';
            """))
            db_columns = [row[0] for row in result.fetchall()]

        # print(f"[green]DB Columns: {db_columns}[/green]")

        df = df[[col for col in df.columns if col in db_columns]]

        df.to_sql(
            name=table_name,
            con=engine,
            schema="imp",
            if_exists="append",
            index=False
        )
        print(f"✅ Data from '{file_path}' appended to table '{table_name}'.")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")





def main():
    """Main function to handle web scraping logic."""
    try:
        session = new_session()

        db_user = "postgres"
        db_password = "123456"
        db_host = "localhost"
        db_port = "5431"
        db_name = "enem"

        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', isolation_level="AUTOCOMMIT")

        with engine.connect() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS imp;"))

            print("[red]Dropping existing table (if exists)...[/red]")
            connection.execute(text("DROP TABLE IF EXISTS imp.chamada_regular;"))

            print("[green]Recreating table...[/green]")
            connection.execute(text("""
                CREATE TABLE imp.chamada_regular (
                    co_ies TEXT,
                    no_ies TEXT,
                    sg_ies TEXT,
                    sg_uf_ies TEXT,
                    no_campus TEXT,
                    co_ies_curso TEXT,
                    no_curso TEXT,
                    ds_turno TEXT,
                    ds_formacao TEXT,
                    qt_vagas_concorrencia TEXT,
                    co_inscricao_enem TEXT,
                    no_inscrito TEXT,
                    no_modalidade_concorrencia TEXT,
                    st_bonus_perc TEXT,
                    qt_bonus_perc TEXT,
                    no_acao_afirmativa_bonus TEXT,
                    nu_nota_candidato TEXT,
                    nu_notacorte_concorrida TEXT,
                    nu_classificacao TEXT,
                    ensino_medio TEXT,
                    quilombola TEXT,
                    deficiente TEXT,
                    tipo_concorrencia TEXT
                );
            """))

        table_name = "chamada_regular"
        institutions = search_api(session)

        print("[bold cyan]Fetched Institutions Data:[/bold cyan]")
        for institution in institutions:
            file_record = search_csv(session, institution)

            if file_record:
                print(f"Institution: {institution.co_ies}, CSV Record: {file_record.no_arquivo}")
                csv_file_path = download_and_save_csv(session, file_record)
                import_csv_file(csv_file_path, table_name, engine)
            else:
                print(f"[yellow]No file record found for Institution {institution.co_ies}[/yellow]")

    except requests.RequestsError as e:
        print(f"[bold red]Request failed:[/bold red] {e}")
    except Exception as e:
        print(f"[bold red]An error occurred:[/bold red] {e}")





if __name__ == "__main__":
    main()