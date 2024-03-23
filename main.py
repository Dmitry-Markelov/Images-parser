from bs4 import BeautifulSoup
import requests
import time
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 

driver = webdriver.Chrome()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept' : '*/*',
}

query = 'car side view'
url = f'https://www.google.com/search?q={query}&udm=2&tbm=isch'

def fetch_images(max_images = 10):
    image_urls = []
    image_count = 0
    driver.get(url)

    while image_count < max_images:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        # time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_count = len(soup.select('img.rg_i'))

    result = soup.select('img.rg_i')[:max_images]
    for img in result:
        src = img.get('src')
        print(src)
        if src:
            image_urls.append(src)
            if len(image_urls) >= max_images:
                break

    driver.quit()
    return image_urls

def download_images(images_urls):
    save_images = 0

    while save_images < len(images_urls):
        src = images_urls[save_images]
        if src and ',' in src:
            head, data = src.split(',', 1)
            file_ext = '.' + head.split(';')[0].split('/')[1]
            plain_data = base64.b64decode(data)
            save_path = 'images/image'

            with open(save_path + str(save_images) + file_ext, "wb") as file:
                file.write(plain_data)
                save_images+=1

img_urls = fetch_images(100)
print(len(img_urls))
download_images(img_urls)