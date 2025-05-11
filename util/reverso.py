from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse

class ReversoHandler:
    def __init__(self):
        self.BASE_URL_CONTEXT = "https://context.reverso.net/translation"

        self.MAX_TRANSLATIONS = 3
        self.MAX_CONTEXTS = 5

        self.driver = self._initialize_driver()


    def _initialize_driver(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--disable-gpu")
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def get_context(self, query: str, lang_to="hebrew", lang_from="english"):

        translations = []
        contexts = []

        encoded_query = urllib.parse.quote_plus(query)
        request_url = f"{self.BASE_URL_CONTEXT}/{lang_to}-{lang_from}/{encoded_query}"

        self.driver.get(request_url)

        # Wait for the translations container to load
        translation_container = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "translations-content"))
        )
        # Extract translations
        extracted_translation_elements = translation_container.find_elements(By.CLASS_NAME, "translation")
        tr_count = 0
        for index, translation_element in enumerate(extracted_translation_elements):
            translations.append(translation_element.get_attribute("data-term"))
            tr_count += 1
            if tr_count >= self.MAX_TRANSLATIONS:
                break

        context_container = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "examples-content"))
        )

        extracted_context_elements = context_container.find_elements(By.CLASS_NAME, "example")
        ex_count = 0
        for index, context_element in enumerate(extracted_context_elements):
            source_element = context_element.find_element(By.CLASS_NAME, "src")
            target_element = context_element.find_element(By.CLASS_NAME, "trg")

            source_example = source_element.text
            target_example = target_element.text

            contexts.append((source_example, target_example))

            ex_count += 1
            if ex_count >= self.MAX_CONTEXTS:
                break

        return translations, contexts


if __name__ == "__main__":
    handler = ReversoHandler()
    print(handler.get_context("java"))
