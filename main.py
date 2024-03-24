import requests
import time
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

driver = webdriver.Chrome()
QUERY = 'car side view'
URL = f'https://www.google.com/search?q={QUERY}&udm=2&tbm=isch'
SAVE_PATH = 'images/image'
MAX_IMAGES = 500
wait = WebDriverWait(driver, 6)

def scroll_page():
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

def fetch_images(max_images = 10):
    elements = []
    image_urls = []
    driver.get(URL)
    index = 0

    while len(elements) < max_images:
        scroll_page()
        time.sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, 'rg_i')

    for element in elements:
        if len(image_urls) >= max_images:
            break
        try:
            element.click()
            img = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'iPVvYb' if 'iPVvYb' else 'sFlh5c')))
            image_urls.append(img.get_attribute('src'))
            download_image(img.get_attribute('src'), index)
            index+=1
            continue
        except:
            image_urls.append(element.get_attribute('src'))
            download_image(element.get_attribute('src'), index)
            index+=1
            continue
    
    driver.quit()
    return image_urls

def download_image(src, index):
    save_path = f'{SAVE_PATH}{index}.jpg'

    with open(save_path, "wb") as file:
        if src.startswith('https'):
            img = requests.get(src, headers=HEADERS)
            file.write(img.content)
        elif src.startswith('data:image'):
            data = src.split(',', 1)[-1]
            plain_data = base64.b64decode(data)
            file.write(plain_data)

def download_images(images_urls):
    for index, src in enumerate(images_urls):
        download_image(src, index)

img_urls = fetch_images(MAX_IMAGES)