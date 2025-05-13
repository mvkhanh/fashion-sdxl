import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import constant as const
import sys
import json
import pandas as pd
from item import ProductItem


def scroll_to_end(driver):
    scroll_increment = 500  # Số pixel mỗi lần cuộn
    scroll_pause_time = 0.5  # Dừng giữa các lần cuộn

    last_height = driver.execute_script("return document.body.scrollHeight")
    current_scroll_position = 0

    while current_scroll_position < last_height:
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        current_scroll_position += scroll_increment
        time.sleep(scroll_pause_time)
        last_height = driver.execute_script("return document.body.scrollHeight")  # Cập nhật chiều cao mới
    
def check_for_popup(driver):
    try:
        close_btn = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-component="ModalCloseButton"]'))
        )
        time.sleep(1)
        close_btn.click()
        time.sleep(1)
    except:
        pass
        
DATA_FILE = '../raw_data.jsonl'
df = pd.read_json(DATA_FILE, lines=True)
seen_products = set(df['url'].unique())
os.environ['PATH'] += 'chromedriver-mac-arm64/chromedriver'

driver = webdriver.Chrome()
driver.implicitly_wait(15)
driver.set_window_size(500, 1000)
driver.set_window_position(0, 0)
driver.get(const.URLS[1])

while True:
    s = set()
    check_for_popup(driver)
    scroll_to_end(driver)
    products = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="productCard"]')
    print(len(products))

    for product in products:
        product_url = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        s.add(product_url)
        
    next_page = driver.find_element(By.CSS_SELECTOR, 'a[data-component="PaginationNextActionButton"]').get_attribute('href')
    s = s - seen_products
    for url in s:
        driver.get(url)
        print(url)
        check_for_popup(driver)
        time.sleep(1)
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//h2[contains(text(), "Sorry, this piece is currently out of stock")]'))
                )
            continue
        except:
            pass
        json_data = driver.find_element(By.CSS_SELECTOR, 'script[type*="application/ld+json"]').get_attribute('innerHTML')
        meta_data = json.loads(json_data)
        category = driver.find_element(By.CSS_SELECTOR, 'button[data-component="DropdownMenuSelectorButtonGhostDark"]').text
        main_type = driver.find_element(By.CSS_SELECTOR, 'a[data-type="category"]').text.strip()
        try:
            sub_type = driver.find_element(By.CSS_SELECTOR, 'a[data-type="subcategory"]').text.strip()
        except:
            sub_type = driver.find_element(By.CSS_SELECTOR, 'a[data-type="brand"]').text.strip()
            main_type, sub_type = sub_type, main_type
        brand = meta_data['brand']['name'].strip()
        name = meta_data['name'].strip()
        price = int(meta_data['offers']['price'])
        currency = meta_data['offers']['priceCurrency'].strip()
        image_urls = [img['contentUrl'] for img in meta_data['image']]
        # time.sleep(1)
        detail_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-component*="AccordionButton"]')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", detail_btn)
        # time.sleep(1)

        try:
            composition = WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located((By.XPATH, '//h4[contains(text(), "Composition")]/following-sibling::p//span'))
            )
        except:
            detail_btn.click()
            time.sleep(1)
            composition = driver.find_elements(By.XPATH, '//h4[contains(text(), "Composition")]/following-sibling::p//span')
            
        composition = [e.text.strip() for e in composition]
        
        try:
            hightlights = WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located((By.XPATH, '//h4[contains(text(), "Highlights")]/following-sibling::ul//li'))
            )
            hightlights = [e.text.strip() for e in hightlights]
        except:
            hightlights = []
            print('No highlights')
        
        ProductItem(url, category, main_type, sub_type, brand, name, price, currency, image_urls, composition, hightlights).save_to_jsonl(DATA_FILE)
        print(f'Save a {sub_type}')
        seen_products.add(url)
        scroll_to_end(driver)
            
    if next_page:
        driver.get(next_page)
        print(next_page)
        
