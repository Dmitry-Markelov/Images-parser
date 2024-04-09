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

driver = webdriver.Firefox()
QUERY = 'car side view'
URL = f'https://www.google.com/search?q={QUERY}&udm=2&tbm=isch'
SAVE_PATH = 'images/image'
MAX_IMAGES = 20
wait = WebDriverWait(driver, 5)

def scroll_page():
    try:
        driver.find_element(By.CLASS_NAME, 'LZ4I').click() #кнопка "Ещё результаты"
    except:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

def fetch_images(max_images = 10):
    elements = []
    image_urls = []
    driver.get(URL)

    while len(elements) < max_images/3:
        scroll_page()
        time.sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, 'rg_i')

    for element in elements:
        if len(image_urls) >= max_images:
            break
        try:
            element.click()
            time.sleep(1)
            img = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'iPVvYb' if 'iPVvYb' else 'sFlh5c')))
            src = img.get_attribute('src')
            if src not in image_urls:
                image_urls.append(src)

            div_element = driver.find_element(By.CLASS_NAME, 'FUJHTc')
            similar_img = div_element.find_elements(By.CLASS_NAME, 'rg_i')
            similar_img[0].click()
            button = wait.until(EC.visibility_of_element_located((By.XPATH, "(//button[contains(@class, 'iM6qI')])[2]")))
            for i in range(0, len(similar_img)):
                try:
                    button.click()

                    test1 = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'iPVvYb' if 'iPVvYb' else 'sFlh5c')))
                    src = test1.get_attribute('src')
                    if src not in image_urls:
                        image_urls.append(src)

                except Exception as e:
                    print("Error:", e)
                    continue
        except:
            src = element.get_attribute('src')
            if src not in image_urls:
                image_urls.append(src)
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
print(img_urls)
download_images(img_urls)