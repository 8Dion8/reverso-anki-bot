from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import urllib.parse
from time import sleep

import logging

class ReversoHandler:
    def __init__(self):
        self.BASE_URL_CONTEXT = "https://context.reverso.net/translation"

        self.MAX_TRANSLATIONS = 3
        self.MAX_CONTEXTS = 6

        self.driver = self._initialize_driver()


    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def get_translations(self, query: str, lang_to: str, lang_from: str):
        translations = []
        encoded_query = urllib.parse.quote_plus(query)
        request_url = f"{self.BASE_URL_CONTEXT}/{lang_to}-{lang_from}/{encoded_query}"

        logging.info(f"Requesting {request_url} for translations")

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

        return translations

    def get_contexts(self, query_from: str, query_to, lang_to: str, lang_from: str):

        contexts = []

        encoded_query = urllib.parse.quote_plus(query_from)
        request_url = f"{self.BASE_URL_CONTEXT}/{lang_to}-{lang_from}/{encoded_query}#{query_to}"

        logging.info(f"Requesting {request_url} for contexts")

        self.driver.get(request_url)
        sleep(2)

        context_container = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "examples-content"))
        )
        example_container = context_container.find_elements(By.CLASS_NAME, "example")
        print(len(example_container))
        ex_count = 0
        for example in example_container:
            try:

                source_element = example.find_element(By.CLASS_NAME, "src")
                target_element = example.find_element(By.CLASS_NAME, "trg")

                source_example = source_element.text
                target_example = target_element.text

                contexts.append((source_example, target_example))

                if (ex_count := ex_count + 1) >= self.MAX_CONTEXTS:
                    break
            except StaleElementReferenceException:
                continue

        return contexts


VALID_LANGUAGES = ["arabic", "german", "english", "spanish", "french", "hebrew", "italian", "japanese", "korean", "dutch", "polish", "portugese", "romanian", "russian", "swedish", "turkish", "ukranian", "chinese"]
