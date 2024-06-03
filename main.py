import requests
import time
import base64
import pymysql
from PIL import Image
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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

# заголовки запроса
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

driver = webdriver.Firefox()

# поисковый запрос
QUERY = 'car side view'
URL = f'https://www.google.com/search?q={QUERY}&udm=2&tbm=isch'

# максимальное количество изображений для загрузки
MAX_IMAGES = 1000

# ожидание загрузки
wait = WebDriverWait(driver, 5)

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

    while len(elements) < max_images/10:
        scroll_page()
        time.sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, 'rg_i')

    for element in elements:
        if len(image_urls) >= max_images:
            break
        try:
            element.click() # нажатие на картинку
            time.sleep(1)
            add_src(index)
            index+=1

            # похожие изображения
            div_element = driver.find_element(By.CLASS_NAME, 'FUJHTc') # группа с похожими изображениями
            similar_img = div_element.find_elements(By.CLASS_NAME, 'rg_i') # похожие изображения

            for i in range(len(similar_img)):
                actions = ActionChains(driver)
                driver.execute_script("arguments[0].scrollIntoView();", similar_img[i]) # прокрутка страницы до similar_img[i]
                actions.key_down(Keys.CONTROL).click(similar_img[i]).key_up(Keys.CONTROL).perform() # открытие элемента в новой вкладке
                driver.switch_to.window(driver.window_handles[-1]) # переключение на следующую вкладку
                add_src(index)
                index+=1
                driver.close() # закрытие вкладки
                driver.switch_to.window(driver.window_handles[0]) # переключение на основную вкладку
        except:
            continue
    
    driver.quit()
    return image_urls

def extract_tags(img_element):
    tags = []
    alt_text = img_element.get_attribute('alt')
    title_text = img_element.get_attribute('title')
    if alt_text:
        tags.append(alt_text)
    if title_text:
        tags.append(title_text)
    return tags

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

# получение массива ссылок
img_urls = fetch_images(MAX_IMAGES)