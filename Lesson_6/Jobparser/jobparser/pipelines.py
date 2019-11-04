# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import re

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

    # salary =re.split(r'[^\d+\s+]+', salary_string)
    answer = {'salary_from': None, 'salary_to': None}

    salary_string = ''.join(salary_string)

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
    if len(salary) == 2:
        answer['salary_from'] = int(salary[0])
        answer['salary_to'] = int(salary[1])
    elif salary_string.split()[0] == 'от':
        answer['salary_from'] = int(salary[0])
    elif salary_string.split().count('до') == 1:
        answer['salary_to'] = int(salary[0])

    return answer

class JobparserPipeline(object):
    # def __init__(self):
    #     client = MongoClient('localhost', 27017)
    #     self.mongo_base = client.VacancyScrapy
    #
    # def process_item(self, item, spider):
    #     if spider.name=='SJru':
    #         item['salary'] = determine_salary(item['salary'])
    #
    #     collection = self.mongo_base[spider.name]
    #     collection.insert_one(item)
    #     return item

    #новая версия
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.VacancyScrapyNew

    def process_item(self, item, spider):

        if spider.name == 'SJru':
            item['salary'] = determine_salary(item['salary'])
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
