from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
mongo_base = client.Mail_data
collection = mongo_base['Yandex']

login = input('Введите адрес электронной почты в домене Яндекса: ')
password = input('Введите пароль к почтовому ящику: ')

driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://mail.yandex.ru')

assert "Яндекс.Почта" in driver.title
button = driver.find_element_by_class_name('HeadBanner-Button-Enter')
button.click()

login_field = driver.find_element_by_id('passp-field-login')
login_field.send_keys(login)
button = driver.find_element_by_class_name('button2_type_submit')
button.click()

# у Яндекса окно ввода пароля всплывает не сразу,
#поэтому необходимо подождать
password_field = WebDriverWait(driver,5).until(
            EC.element_to_be_clickable((By.ID ,'passp-field-passwd')))

password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)

def get_data(page, xpath_expr):
    text_element = WebDriverWait(page, 10).until( EC.presence_of_element_located((By.XPATH, xpath_expr))).text
    return text_element

def get_email_data(page):
    item = {}

    item['sender_email'] = get_data(page, '//span[contains(@class,"mail-Message-Sender-Email")]')
    item['sender_name'] = get_data(page, '//span[contains(@class,"ns-view-message-head-sender-name")]')
    item['mail_date'] = get_data(page, '//div[contains(@class,"ns-view-message-head-date")]')
    item['mail_theme'] = get_data(page, '//div[contains(@class,"mail-Message-Toolbar-Subject")]')
    item['mail_text'] = get_data(page, '//div[contains(@class,"mail-Message-Body-Content")]')

    return item

#раскроем список писем до самого конца, используя нажатие на кнопку "Ещё письма"
while True:
    try:
        button_next_letters = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'mail-MessagesPager-button')))
        button_next_letters.click()
    except Exception as e:
        print('Писем больше нет или что-то пошло не так')
        break

#получаем список писем
letters_len = len(driver.find_elements_by_xpath('//div[contains(@class, "mail-MessageSnippet-Wrapper")]/a'))

for count in range(letters_len):
    #смотрим доступность списка писем
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "mail-MessageSnippet-Wrapper")]/a')))
    letters = driver.find_elements_by_xpath('//div[contains(@class, "mail-MessageSnippet-Wrapper")]/a')

    #проходим в письмо и получаем данные письма
    letters[count].click()

    item = get_email_data(driver)
    print(item)

    #записываем item в коллекцию
    try:
        collection.insert_one(item)
    except Exception as e:
        print(e)
        print('Не удалось записать документ в коллекцию')
    driver.back()

'''
Ещё у яндекса есть такое решение, как "цепочка писем". Грубо говоря, идущие подряд письма
от одного получателя, отображаются как одно письмо, которое требует щелчка мышью, при этом раскрывается
ветвь писем, и необходимо выполнять уже именно обход этой ветви. Мне такое не встретилось, 
но подобный случай обработать необходимо
'''

'''В общем, хотел попробовать зайти в первое письмо и последовательно переходить по письмам,
нажимая кнопку "след." (следующее письмо). В процессе тестирования выяснилось,
что эта кнопка работает не совсем корректно, и на определенном письме она зацикливается, 
вместо перехода на следующее письмо переходит на предыдущее, потом опять на следующее и т.д. по кругу.
Файл с логами, которые выводил, приложил. По ним видно, что начиная с определенного момента ITEMы писем
начинают повторяться. Проверил это поведение кнопки в браузере - аналогичная ситуация, на определенном письме
кнопка перенаправляет не на следующее, а на предыдущее письмо.
Написал в техподдержку яндекса.
Используемый код ниже - закомментировал, чтобы было видно, как пытался решить задачу.

#получим ссылку на первое письмо
first_letter = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (By.CLASS_NAME, 'ns-view-messages-item-wrap')
    )
)
first_letter.click()
while True:
    try:

        current_url = driver.current_url

        item = get_email_data(driver)
        print('получили данные')
        collection.insert_one(item)
        print(item)

        next_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[text()="след."]')))

        print('жмём на кнопку')
        next_button.click()
        print(next_button.id)

        WebDriverWait(driver, 15).until(EC.url_changes(current_url))

    except Exception as e:
        print(e)
        print('Кончились письма или что-то пошло не так')
        break
'''

driver.quit()





