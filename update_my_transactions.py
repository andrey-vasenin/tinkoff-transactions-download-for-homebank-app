import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle


# Homebank app for some reason does not want to load russian characters correctly
# So here is a rule to transliterate them
def transliterate_russian_to_latin(text):
    # Basic transliteration dictionary for Russian to Latin
    translit_dict = {
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

    transliterated_text = ''.join(translit_dict.get(char, char) for char in text)
    return transliterated_text

# Tinkoff specific paramaters
tinkoff_login_url = "https://www.tinkoff.ru/login/" # Tinkoff login page
tinkoff_transactions_page = "https://www.tinkoff.ru/events/feed/" # Taknoff page with all the transactions
btn_text = "Выгрузить все операции в OFX" # Name of the button to be pressed eventually

# Define paths
# Get the full path of the currently running script
script_path = os.path.abspath(__file__)
current_folder = os.path.dirname(script_path)
CHROME_DRIVER_PATH =  os.path.join(current_folder, 'chromedriver.exe')
profile_path = os.path.join(current_folder, 'profile') # specify the directory to keep you new chrome profile specific for this task
download_dir = os.path.join(current_folder, 'downloads')  # specify the directory where you want to download the file

# Set up Chrome preferences
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,  # To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # To auto download PDFs
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument(f"user-data-dir={profile_path}")

if __name__ == "__main__":
    # Check if the required folders do not exist and create them
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    # Find existing .ofx files to be able to detect a downloaded .ofx file later
    existing_ofx_files = set([f for f in os.listdir(download_dir) if f.endswith('.ofx')])

    # Start a new instance of a web browser
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)

    # STEP 1. Log in
    # Navigate to the bank's login page
    browser.get(tinkoff_login_url)
    print("Entered")

    # STEP 2. After logging in, wait for the main page to load
    # Wait for you to manually log in (e.g., wait for 60 seconds or any other mechanism)
    operations_link = WebDriverWait(browser, 60).until(
        EC.presence_of_element_located((By.XPATH, "//a[@data-item-name='Операции']"))
    )
    time.sleep(5)

    # STEP 3. Navigate to the transactions page and initialize download
    browser.get(tinkoff_transactions_page)

    # Wait for the export button to appear and click on it
    button = WebDriverWait(browser, 60).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-qa-id='export']"))
    )
    button.click()

    # Wait for the OFX export button to appear and launch the download by clicking it
    button2 = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.XPATH, f"//span[@data-qa-file='ContextMenuItem' and text()='{btn_text}']"))
    )
    button2.click()

    # STEP 4. Wait for the OFX file to download in the `download_dir` directory
    downloaded_file = None
    while not downloaded_file:
        current_ofx_files = set([f for f in os.listdir(download_dir) if f.endswith('.ofx')])
        new_files = current_ofx_files - existing_ofx_files
        if new_files:
            downloaded_file = new_files.pop()
        time.sleep(1)
    print("Downloaded:", downloaded_file)

    # STEP 5. Close the browser
    browser.quit()

    # Transliterate the downloaded OFX file
    filename = os.path.join(download_dir, downloaded_file)
    split_filename = filename.split('.')
    name = '.'.join(split_filename[:-1])
    extension = split_filename[-1]
    output_filename = name + '_transliterated.' + extension
    print(f"Transliterating {filename} ")#into {output_filename}")
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        transliterated_content = transliterate_russian_to_latin(content)

    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(transliterated_content)

    print(f"Transliterated content saved to {output_filename}")
