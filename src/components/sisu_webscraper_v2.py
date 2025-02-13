# import os
# from pydantic import BaseModel, HttpUrl
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json

# target_link = "https://sisu.mec.gov.br/#/selecionados"

# class Institution(BaseModel):
#     co_ies: str
#     no_ies: str
#     sg_ies: str
#     sg_uf: str
#     co_municipio: str
#     no_municipio: str
#     no_sitio_ies: str


# class WebDriverContext:
#     """Context manager for Selenium WebDriver."""
#     def __init__(self, driver):
#         self.driver = driver

#     def __enter__(self):
#         return self.driver

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.driver.quit()



# def driver_path() -> str:
#     chrome_driver_relative_path = "data/chromedriver-win64/chromedriver.exe"
#     chrome_driver_path = os.path.abspath(chrome_driver_relative_path)

#     if os.path.exists(chrome_driver_path):
#         print(f"✅ ChromeDriver found at: {chrome_driver_path}")
#     else:
#         print(f"❌ ChromeDriver NOT found at: {chrome_driver_path}\nPlease check the file location!")

#     return chrome_driver_path


# def create_driver() -> webdriver.Chrome:
#     options = Options()
#     options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

#     service = Service(driver_path())
#     return webdriver.Chrome(service=service, options=options)


# def fetch_xhr_request(driver: webdriver, api_param: str):
#     logs = driver.get_log("performance")

#     # Process logs to extract API requests
#     for log in logs:
#         log_data = json.loads(log["message"])  # Convert log to JSON
#         try:
#             request_url = log_data["message"]["params"]["request"]["url"]  # Extract request URL
#             if "api" in request_url and api_param in request_url:  # Filter API requests (adjust as needed)
#                 print(f"API Request: {request_url}")
#         except KeyError:
#             continue  # Skip logs that don’t have request info


# def fetch_call_request(driver: webdriver):
#     try:
#         # Wait for the dropdown to be interactable and open it
#         dropdown = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, "ng-select"))
#         )
#         dropdown.click()  # Open dropdown

#         # Wait for the first option to be available and select it
#         first_option = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ng-option"))
#         )
#         first_option.click()  # Select the first option
#         print("✅ Dropdown populated successfully.")

#     except Exception as e:
#         print(f"❌ Error populating dropdown: {e}")

#     button = driver.find_element(By.XPATH, "//div[@class='bt_pesquisa']/a")
#     button.click()
#     fetch_xhr_request(driver, "chamada_regular")



# def main() -> None:
#     with WebDriverContext(create_driver()) as driver:
#         driver.get(target_link)

#         import time
#         time.sleep(1)

#         fetch_xhr_request(driver, "instituicoes")
#         fetch_call_request(driver)

#         time.sleep(5)

#     return


# if __name__ == "__main__":
#     main()
