# import os
# from pydantic import BaseModel, HttpUrl
# from rich import print
# from curl_cffi import requests
# from typing import List, Optional

# # Define a model to parse the JSON response
# class Institution(BaseModel):
#     co_ies: str
#     no_ies: str
#     sg_ies: str
#     sg_uf: str
#     co_municipio: str
#     no_municipio: str
#     no_sitio_ies: str

# class FileRecord(BaseModel):
#     co_arquivo: str
#     co_edicao: str
#     co_ies: str
#     no_arquivo: str
#     ds_caminho_arquivo: HttpUrl
#     tp_arquivo: str
#     dt_inclusao: str
#     dt_alteracao: Optional[str]
#     st_ativo: str


# def new_session():
#     session = requests.Session(impersonate="chrome", proxy=os.getenv("stickyproxy"))
#     return session

# def search_api(session: requests.Session) -> List[Institution]:
#     url = "https://sisu-api.sisu.mec.gov.br/api/v1/oferta/instituicoes"
#     resp = session.get(url)
#     resp.raise_for_status()
#     institutions = [Institution(**item) for item in resp.json()]
#     return institutions

# def search_csv(session: requests.Session, item: Institution) -> List[Institution]:
#     url = "https://sisu-api.sisu.mec.gov.br/api/v1/arquivo/{item.co_ies}/chamada_regular"
#     resp = session.get(url)
#     resp.raise_for_status()
#     csv = [FileRecord(**item) for item in resp.json()]
#     return csv

# def main():
#     """Main function to handle web scraping logic."""
#     try:
#         session = new_session()
#         institutions = search_api(session)

#         print("[bold cyan]Fetched Institutions Data:[/bold cyan]")
#         for institution in institutions:
#             csv = search_csv(session, institution)
#             print(institution.co_ies)
#             print(csv.co_ies)


#     except requests.RequestError as e:
#         print(f"[bold red]Request failed:[/bold red] {e}")
#     except Exception as e:
#         print(f"[bold red]An error occurred:[/bold red] {e}")

# if __name__ == "__main__":
#     main()