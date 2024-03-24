import requests
import time
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept' : '*/*',
}

query = 'car side view'
url = f'https://www.google.com/search?q={query}&udm=2&tbm=isch'

def scroll_page():
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

def fetch_images(max_images = 10):
    elements = []
    image_urls = []
    driver.get(url)

    while len(elements) < max_images:
        scroll_page()
        time.sleep(1)

        elements = driver.find_elements(By.CLASS_NAME, 'rg_i')

    for element in elements:
        if len(image_urls) >= max_images:
            break
        try:
            element.click()
            time.sleep(1)
            img = driver.find_element(By.CLASS_NAME, 'iPVvYb' if 'iPVvYb' else 'sFlh5c')
            image_urls.append(img.get_attribute('src'))
            continue
        except:
            image_urls.append(element.get_attribute('src'))
            continue
    
    driver.quit()
    return image_urls

def download_images(images_urls):
    save_images = 0
    save_path = 'images/image'

    while save_images < len(images_urls):
        src = images_urls[save_images]

        with open(save_path + str(save_images) + '.jpg', "wb") as file:
            if src.startswith('https'):
                img = requests.get(src)
                file.write(img.content)

            elif src.startswith('data:image'):
                data = src.split(',', 1)[-1]
                plain_data = base64.b64decode(data)
                file.write(plain_data)
            else: continue
            save_images+=1

img_urls = fetch_images(505)
download_images(img_urls)