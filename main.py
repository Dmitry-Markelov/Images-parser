import requests
import time
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# заголовки запроса
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

driver = webdriver.Firefox()

# поисковый запрос
QUERY = 'car side view'
URL = f'https://www.google.com/search?q={QUERY}&udm=2&tbm=isch'

# путь для сохраниения изображений
SAVE_PATH = 'images/image'

# максимальное количество изображений для загрузки
MAX_IMAGES = 1000

# ожидание загрузки
wait = WebDriverWait(driver, 1)

def scroll_page():
    try:
        driver.find_element(By.CLASS_NAME, 'LZ4I').click() # кнопка "Ещё результаты"
    except:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) # прокрутка вниз

def fetch_images(max_images = 10):
    elements = [] # массив img
    image_urls = [] # массив src
    driver.get(URL)
    index = 0

    def add_src(): # поиск картинки и проверка на существующий src
        try:
            img = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'iPVvYb')))
        except:
            img = driver.find_element(By.CLASS_NAME, 'sFlh5c')
        src = img.get_attribute('src')
        if src not in image_urls:
            image_urls.append(src) # добавление ссылки в массив

    while len(elements) < max_images/3:
        scroll_page()
        time.sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, 'rg_i')

    for element in elements:
        if len(image_urls) >= max_images:
            break

        element.click() # нажатие на картинку
        time.sleep(1)
        add_src()

        # похожие изображения
        div_element = driver.find_element(By.CLASS_NAME, 'FUJHTc') # группа с похожими изображениями
        similar_img = div_element.find_elements(By.CLASS_NAME, 'rg_i') # похожие изображения
        similar_img[0].click() # нажатие на похожую картинку
        add_src()
        
        # кнопка следующего изображения
        next_button = wait.until(EC.visibility_of_element_located((By.XPATH, "(//button[contains(@class, 'iM6qI')])[2]")))
        
        for i in range(0, len(similar_img)):
            try:
                next_button.click() # следующее изображение
                add_src()
            except Exception:
                continue
    
    driver.quit()
    return image_urls

def download_image(src, index): # скачивание изображения по URL
    save_path = f'{SAVE_PATH}{index}.jpg'

    with open(save_path, "wb") as file:
        if src.startswith('https'): # проверка, начинается ли URL с 'https'
            img = requests.get(src, headers=HEADERS)
            file.write(img.content)
        elif src.startswith('data:image'): # проверка, начинается ли URL с 'https'
            data = src.split(',', 1)[-1]
            plain_data = base64.b64decode(data)
            file.write(plain_data)

def download_images(images_urls): # скачивание всех изображений из массива
    for index, src in enumerate(images_urls):
        download_image(src, index)

# получение массива ссылок
img_urls = fetch_images(MAX_IMAGES)

# скачивание изображений
download_images(img_urls)
