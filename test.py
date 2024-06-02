import os
import requests
import time
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
QUERY = 'car side view'

# заголовки запроса
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/122.0.0.0 Safari/537.36'
}

driver = webdriver.Firefox()

# поисковый запрос
URL = f'https://www.google.com/search?q={QUERY}&udm=2&tbm=isch'



def scroll_page():
    try:
        driver.find_element(By.CLASS_NAME, 'LZ4I').click() # кнопка "Ещё результаты"
    except:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) # прокрутка вниз


def extract_tags(img_element):
    tags = []
    alt_text = img_element.get_attribute('alt')
    title_text = img_element.get_attribute('title')
    if alt_text:
        tags.append(alt_text)
    if title_text:
        tags.append(title_text)
    return tags

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/122.0.0.0 Safari/537.36'
}

import requests

def download_image(src, index):
    try:
        save_path = f'images/image{index}.jpg'

        with open(save_path, "wb") as file:
            if src.startswith('https'):
                img = requests.get(src, headers=HEADERS)
                file.write(img.content)
            elif src.startswith('data:image'):
                data = src.split(',', 1)[-1]
                plain_data = base64.b64decode(data)
                file.write(plain_data)
    except:
        print('Не удалось скачать изображение')

import pymysql

# Параметры подключения к базе данных
db_config = {
    'host': 'localhost',
    'user': 'username',
    'password': 'password',
    'database': 'mydb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Подключение к базе данных
connection = pymysql.connect(**db_config)

from PIL import Image
from io import BytesIO

def store_image_in_db(src, index, tags):
    try:
        if src.startswith('https'):
            img = requests.get(src, headers=HEADERS).content
        elif src.startswith('data:image'):
            data = src.split(',', 1)[-1]
            img = base64.b64decode(data)
        else:
            print('Не удалось получить изображение')
            return

        # Извлечение метаданных изображения
        image = Image.open(BytesIO(img))
        width, height = image.size
        size = len(img)
        format = image.format

        # Сохранение метаданных и URL в базу данных
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO image (url, name, width, height, size, format)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (src, f'image{index}', width, height, size, format))
            image_id = cursor.lastrowid

            # Сохранение тегов в базу данных
            for tag in tags:
                sql = """
                INSERT INTO tags (tag_name)
                VALUES (%s)
                ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
                """
                cursor.execute(sql, (tag,))
                tag_id = cursor.lastrowid

                sql = """
                INSERT INTO image_tag (id_image, id_tag)
                VALUES (%s, %s)
                """
                cursor.execute(sql, (image_id, tag_id))

        connection.commit()
    except Exception as e:
        print(f'Не удалось сохранить изображение в базу данных: {e}')

wait = WebDriverWait(driver, 5)

elements = []  # Массив img элементов
image_urls = []  # Массив src атрибутов
driver.get(URL)
index = 0

def add_src(index):
    try:
        img = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'iPVvYb')))
        src = img.get_attribute('src')
        if src not in image_urls:
            image_urls.append(src)
            tags = extract_tags(img)
            store_image_in_db(src, index, tags)
    except Exception as e:
        print(f'Не удалось найти изображение: {e}')