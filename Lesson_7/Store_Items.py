from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests
from pymongo import MongoClient


def get_goods_data(product):
    item = {}

    product_link = product.find_element_by_class_name('ui-link').get_attribute('href')
    product_name = product.find_element_by_class_name('ui-link').text
    product_information = product.find_element_by_class_name('product-info__title-description').text
    product_price = product.find_element_by_class_name('product-price__current').text

    print(f'Ссылка на товар: {product_link}')
    print(f'Наименование товара: {product_name}')
    print(f'Информация о товаре: {product_information}')
    print(f'Цена товара: {product_price}')

    item['link'] = product_link
    item['name'] = product_name
    item['information'] = product_information
    item['price'] = product_price
    return item

client = MongoClient('localhost', 27017)
mongo_base = client.Goods_data
collection = mongo_base['DNS-shop']

keywords = input('Введите ключевую фразу для поиска товаров: ')
pages_count = int(input('Введите количество страниц поиска: '))

#магазин, где будем получать информацию о товарах - dns-shop.ru
driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://www.dns-shop.ru/')

#ищем поле поиска товаров
WebDriverWait(driver,10).until(
    EC.element_to_be_clickable((By.XPATH ,'//nav[@id="header-search"]//input[@data-role="search-input"]')))

search_field = driver.find_element_by_xpath('//nav[@id="header-search"]//input[@data-role="search-input"]')
# search_field.click()

search_field.send_keys(keywords)

#нажимаем значок лупы - "найти"
search_icon = driver.find_element_by_xpath(
    '//nav[@id="header-search"]//span[contains(@class,"ui-input-search__icon ui-input-search__icon_search")]')
search_icon.click()

page_number=1
while True:
    if page_number <= pages_count:
        try:
            #скроллим страницу вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            #вынужден поставить это, поскольку возникает ошибка:
            # Message: element click intercepted: Element <button...</button> is not clickable at point (1099, 266).
            # Other element would receive the click: <div class="loader-container"...
            #Это значит, что на момент щелчка кнопка перекрывается каким-то другим элементом, несмотря на то, что условием
            #её поиска ранее было element_to_be_clickable
            time.sleep(1)

            #Ищем кнопку "Показать ещё"
            button_next_items = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'pagination-widget__show-more-btn')))

            button_next_items.click()

            page_number +=1
        except Exception as e:
            print(e)
            print('Дошли до последней страницы или что-то пошло не так')
            break
    else:
        break

#Формируем список товаров
goods = driver.find_elements_by_xpath("//div[@class='products-list__content']//div[@data-id='catalog-item']")
for good in goods:
    time.sleep(3)
    item = get_goods_data(good)
    try:
        collection.insert_one(item)
    except Exception as e:
        print(e)
        print('Не удалось записать документ в коллекцию')
    driver.back()

