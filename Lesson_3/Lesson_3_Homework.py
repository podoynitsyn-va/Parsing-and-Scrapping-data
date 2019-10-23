from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
import Insert_vacancies_to_MongoDB

def clear_link(link, website):
    '''
    Функция убирает из ссылки лишние параметры,
    несущественные для работы.
    '''
    link = link[:link.find('//')] + '//' + link[link.find(website):link.find('?')]
    return link


def determine_salary(salary_string):
    '''
    Функция выделяет вилку заработной платы
    из строки с размером заработной платы.
    На вход подаётся строка зарплаты вида:
    "от 10 до 50"
    "от 10"
    "до 50"
    "по договоренности"
    '''

    # определим числа, которые содержатся в строке зарплаты
    salary = re.findall(r'[0-9\s]+', salary_string)
    # уберём html-неразрывный пробел между разрядами числа
    salary = [s.replace('\xa0', '') for s in salary]

    '''
    Если в salary 2 элемента, то в качестве начала и окончания вилки берем salary[0] и salary[1].
    Если в salary 1 элемент, то если строка salary_string начинается с 'от',
    то в качестве начала вилки используем salary[0].
    А если в строке salary_string присутствует слово 'до',
    то в качестве окончания вилки используем salary[0].
    Если же salary не содержит числовых элементов, то записываем None в начало и конец вилки
    '''
    answer = {'salary_from': None, 'salary_to': None}
    if len(salary) == 2:
        answer['salary_from'] = int(salary[0])
        answer['salary_to'] = int(salary[1])
    elif salary_string.split()[0] == 'от':
        answer['salary_from'] = int(salary[0])
    elif salary_string.split().count('до') == 1:
        answer['salary_to'] = int(salary[0])
    return answer


def get_superjob_data(keyword, link):
    link_origin = 'https://www.superjob.ru'
    html = requests.get(link).text
    parsed_html = bs(html, 'html.parser')

    vacancy_list = parsed_html.findAll('div', {'class': 'f-test-vacancy-item'})

    # определим ссылку на следующую страницу. Это ссылка на кнопку "Далее"
    next_link = link_origin + parsed_html.find('a', {'rel': 'next'})['href']

    # создадим списки с данными, которые будем использовать в качестве столбцов датафрейма
    list_vacancy_link = []
    list_vacancy_text = []
    list_vacancy_company = []
    list_vacancy_place = []
    list_salary_from = []
    list_salary_to = []

    for vacancy in vacancy_list:
        # ищем дочерние элементы вакансии
        vacancy_info = vacancy.find('div', {'class': '_2g1F-'}).findChild()

        # помимо ссылок на вакансии могут быть ещё и ссылки спонсоров. Надо их отфильтровать
        get_link = re.search('.*vakansii.*', vacancy_info.find('a')['href'])

        # определяем вакансию только если ссылка действительно на вакансию
        if get_link is not None:
            vacancy_link = link_origin + re.search('.*vakansii.*', vacancy_info.find('a')['href']).group(0)
            vacancy_text = vacancy_info.find('a').find('div').getText()
            try:
                vacancy_firm = vacancy_info.find('a', {'target': '_self'}).getText()
            except:
                vacancy_firm = None

            # местонахождение - последний элемент массива
            place = vacancy_info.find('span', {'class': 'f-test-text-company-item-location'}).getText().split()[-1]

            # получим всю строку, отвечающую за зарплату
            salary = vacancy_info.find('span', {'class': 'f-test-text-company-item-salary'}).getText()

            salary_dict = determine_salary(salary.strip())

            # добавим полученные данные в списки
            list_vacancy_link.append(vacancy_link)
            list_vacancy_text.append(vacancy_text)
            list_vacancy_company.append(vacancy_firm)
            list_vacancy_place.append(place)
            list_salary_from.append(salary_dict['salary_from'])
            list_salary_to.append(salary_dict['salary_to'])

            # загрузим списки в датафрейм
    vacancy_info = pd.DataFrame({'vacancy_link': list_vacancy_link,
                                 'vacancy_text': list_vacancy_text,
                                 'vacancy_company': list_vacancy_company,
                                 'vacancy_place': list_vacancy_place,
                                 'salary_from': list_salary_from,
                                 'salary_to': list_salary_to})

    vacancy_info['website'] = 'www.superjob.ru'
    return_data = {'data': vacancy_info, 'next_link': next_link}
    return return_data


def get_hh_data(keyword, link):
    link_origin = 'https://www.hh.ru'
    headers = {'Accept': '*/*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
    html = requests.get(link, headers=headers).text
    parsed_html = bs(html, 'html.parser')

    vacancy_list = parsed_html.findAll('div', {'data-qa': 'vacancy-serp__vacancy'})

    # определим ссылку на следующую страницу. Это ссылка на кнопку "Далее"
    next_link = link_origin + parsed_html.find('a', {'data-qa': 'pager-next'})['href']

    # создадим списки с данными, которые будем использовать в качестве столбцов датафрейма
    list_vacancy_link = []
    list_vacancy_text = []
    list_vacancy_company = []
    list_vacancy_place = []
    list_salary_from = []
    list_salary_to = []

    for vacancy in vacancy_list:
        # подчистим ссылку на вакансию
        vacancy_link = clear_link(vacancy.find('a', {'class': 'bloko-link'})['href'], 'hh.ru')

        vacancy_text = vacancy.find('a', {'class': 'bloko-link'}).getText()
        vacancy_firm = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).getText()
        vacancy_place = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).getText()
        try:
            salary_string = vacancy.find('div', {'class': 'vacancy-serp-item__compensation'}).text
            salary_dict = determine_salary(salary_string)
        except:
            salary_dict = {'salary_from': None, 'salary_to': None}

        # добавим полученные данные в списки
        list_vacancy_link.append(vacancy_link)
        list_vacancy_text.append(vacancy_text)
        list_vacancy_company.append(vacancy_firm)
        list_vacancy_place.append(vacancy_place)
        list_salary_from.append(salary_dict['salary_from'])
        list_salary_to.append(salary_dict['salary_to'])

        # загрузим списки в датафрейм
    vacancy_info = pd.DataFrame({'vacancy_link': list_vacancy_link,
                                 'vacancy_text': list_vacancy_text,
                                 'vacancy_company': list_vacancy_company,
                                 'vacancy_place': list_vacancy_place,
                                 'salary_from': list_salary_from,
                                 'salary_to': list_salary_to})

    vacancy_info['website'] = 'www.hh.ru'
    return_data = {'data': vacancy_info, 'next_link': next_link}
    return return_data


#####################################################################################################
#                                    ТЕКСТ ОСНОВНОЙ ПРОГРАММЫ                                       #
#####################################################################################################

keyword = input('Введите ключевое слово, по которому будет выполняться поиск подходящих вакансий:  ')
n_pages = int(input('Введите количество страниц поиска:  '))
salary_from = int(input('Введите размер заработной платы, '
                        'начиная от которого будем показывать вакансии:  '))

# основной датафрейм vacancy_list - к нему будем присоединять результаты обхода страниц
vacancy_list = pd.DataFrame({'vacancy_link': [],
                             'vacancy_text': [],
                             'vacancy_company': [],
                             'vacancy_place': [],
                             'salary_from': [],
                             'salary_to': []})
# ссылка на первую страницу
# Пришлось использовать параметр geo для обхода автоподстановки местоположения
link_superjob = f'https://www.superjob.ru/vacancy/search/?keywords={keyword}&geo%5Bc%5D%5B0%5D=1'

link_hh = link = f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={keyword}'

page = 1
while page <= n_pages:
    # Получим данные superjob
    data = get_superjob_data(keyword, link_superjob)
    vacancy_info = data['data']

    # на следующем шаге цикла вместо первоначальной ссылки используем ссылку на следующую страницу
    link_superjob = data['next_link']

    # добавляем полученные данные к vacancy_list
    vacancy_list = pd.concat([vacancy_list, vacancy_info], axis=0, ignore_index=True, sort=False)

    # Получим данные hh
    data = get_hh_data(keyword, link_hh)
    vacancy_info = data['data']

    # на следующем шаге цикла вместо первоначальной ссылки используем ссылку на следующую страницу
    link_hh = data['next_link']

    # добавляем полученные данные к vacancy_list
    vacancy_list = pd.concat([vacancy_list, vacancy_info], axis=0, ignore_index=True, sort=False)

    page += 1

vacancy_list.to_csv(f'{keyword}_Vacancy_SJ_HH.csv', encoding='utf-8-sig')

Insert_vacancies_to_MongoDB.insert_MongoDB(vacancy_list, 'VacansiesSJHH', salary_from)
