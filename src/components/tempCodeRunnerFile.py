import os
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class WebDriverContext:
    """Context manager for Selenium WebDriver."""
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()


def driver_path() -> str:
    chrome_driver_relative_path = "data/chromedriver-win64/chromedriver.exe"
    chrome_driver_path = os.path.abspath(chrome_driver_relative_path)

    if not os.path.exists(chrome_driver_path):
        raise FileNotFoundError(f"❌ ChromeDriver NOT found at: {chrome_driver_path}\nPlease check the file location!")

    logging.info(f"✅ ChromeDriver found at: {chrome_driver_path}")
    return chrome_driver_path


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    service = Service(driver_path())
    return webdriver.Chrome(service=service, options=options)


def extract_api_requests(logs):
    """Extract API requests from performance logs."""
    for log in logs:
        try:
            log_data = json.loads(log["message"])  # Convert log to JSON
            request_url = log_data["message"]["params"]["request"]["url"]  # Extract request URL
            
            if "api" in request_url and "instituicoes" in request_url:  # Filter API requests (adjust as needed)
                logging.info(f"API Request: {request_url}")

        except (KeyError, json.JSONDecodeError):
            continue  # Skip logs that don’t have request info


def main() -> None:
    target_link = "https://sisu.mec.gov.br/#/selecionados"

    with WebDriverContext(create_driver()) as driver:
        driver.get(target_link)

        # Wait for logs to be available instead of using sleep
        WebDriverWait(driver, 3).until(lambda d: len(d.get_log("performance")) > 0)

        logs = driver.get_log("performance")
        extract_api_requests(logs)

        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='bt_pesquisa']/a"))
            )
            button.click()
            logging.info("🔘 Clicked search button successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to click button: {e}")

        WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")


if __name__ == "__main__":
    main()
