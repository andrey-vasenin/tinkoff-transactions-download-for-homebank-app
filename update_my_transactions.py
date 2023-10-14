import os
import time
import logging
from typing import Tuple, Set
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a new logger named 'ogger'
logger = logging.getLogger('Tinkoff_Update')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

TINKOFF_LOGIN_URL = "https://www.tinkoff.ru/login/"
TINKOFF_TRANSACTIONS_PAGE = "https://www.tinkoff.ru/events/feed/"
BTN_TEXT = "Выгрузить все операции в OFX"

# Homebank app for some reason does not want to load russian characters correctly
# So here is a rule to transliterate them
TRANSLIT_DICT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
    'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya',
    # Add uppercase
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
    'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K',
    'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts',
    'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
    'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}


def transliterate_russian_to_latin(text: str) -> str:
    return ''.join(TRANSLIT_DICT.get(char, char) for char in text)


def setup_directories(current_folder: str) -> Tuple[str, str]:
    profile_path = os.path.join(current_folder, 'profile')
    download_dir = os.path.join(current_folder, 'downloads')

    os.makedirs(profile_path, exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)

    return profile_path, download_dir


def setup_webdriver(chrome_driver_path: str, profile_path: str,
                    download_dir: str) -> webdriver.Chrome:
    chrome_options = ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument(f"user-data-dir={profile_path}")

    service = ChromeService(executable_path=chrome_driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)


def wait_for_element(browser: webdriver.Chrome, value: str, timeout: int = 60) -> WebElement:
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.XPATH, value)), "Unable to locate element")


def download_transaction_file(browser: webdriver.Chrome, tinkoff_transactions_page: str,
                              btn_text: str) -> None:
    browser.get(tinkoff_transactions_page)

    button = wait_for_element(browser, "//div[@data-qa-id='export']")
    button.click()

    button2 = wait_for_element( 
        browser, f"//span[@data-qa-file='ContextMenuItem' and text()='{btn_text}']", 30)
    button2.click()


def find_downloaded_file(download_dir: str, existing_ofx_files: Set[str]) -> str:
    while True:
        current_ofx_files = {f for f in os.listdir(
            download_dir) if f.endswith('.ofx')}
        new_files = current_ofx_files - existing_ofx_files
        if new_files:
            return new_files.pop()
        time.sleep(1)


def wait_for_download_completion(download_dir: str, existing_files: Set[str]) -> str:
    while True:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - existing_files
        for new_file in new_files:
            file_path = os.path.join(download_dir, new_file)
            if not os.path.exists(file_path):
                # Skip if the file no longer exists (e.g., if it was a temporary file that has been renamed or deleted)
                continue
            if new_file.endswith('.tmp'):
                # Skip temporary files
                continue
            # Check if the file size is changing or if it's still being written to
            initial_size = os.path.getsize(file_path)
            time.sleep(1)  # wait for a short period before checking the size again
            final_size = os.path.getsize(file_path)
            if initial_size == final_size:
                return new_file
        time.sleep(1)  # wait for a short period before checking for new files again


def transliterate_file(filename: str) -> str:
    split_filename = filename.split('.')
    name = '.'.join(split_filename[:-1])
    extension = split_filename[-1]
    output_filename = name + '_transliterated.' + extension

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        transliterated_content = transliterate_russian_to_latin(content)

    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(transliterated_content)

    return output_filename


def main() -> None:
    script_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(script_path)
    chrome_driver_path = os.path.join(current_folder, 'chromedriver.exe')

    profile_path, download_dir = setup_directories(current_folder)
    browser = setup_webdriver(chrome_driver_path, profile_path, download_dir)
    existing_ofx_files = {f for f in os.listdir(
        download_dir) if f.endswith('.ofx')}

    browser.get(TINKOFF_LOGIN_URL)
    logger.info("Please log in")
    # Assumes user logs in manually within 60 seconds
    wait_for_element(browser, "//a[@data-item-name='Операции']")
    logger.info("Logged in")

    download_transaction_file(browser, TINKOFF_TRANSACTIONS_PAGE, BTN_TEXT)
    downloaded_file = wait_for_download_completion(download_dir, existing_ofx_files)
    logger.info(f"Downloaded {downloaded_file}")

    browser.quit()

    filename = os.path.join(download_dir, downloaded_file)
    output_filename = transliterate_file(filename)
    logger.info(f"Transliterated content is saved into {output_filename}")


if __name__ == "__main__":
    main()
