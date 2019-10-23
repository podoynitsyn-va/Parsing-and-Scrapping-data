from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)

#1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
# и реализовать функцию, записывающую собранные вакансии в созданную БД.
def insertAll(vacancy_DF, vacancies):
    vacancies.insert_many(vacancy_DF.to_dict('records'))

#2) Написать функцию, которая производит поиск
# и выводит на экран вакансии с заработной платой больше введенной суммы
def find_gte_salary(vacancies, salary_value):
    print(f'Всего вакансий: {vacancies.count()}')
    vacancy_list = vacancies.find({'salary_from': {'$gte': salary_value}}, {'vacancy_link', 'vacancy_text', 'salary_from', 'salary_to'}).sort('vacancy_link')
    print(f'Вакансий с зарплатой больше {salary_value}: {vacancy_list.count()}')
    for vacancy in vacancy_list:
        pprint(vacancy)

#3*)Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
def insert_new(vacancy_DF, vacancies):
    print(f'Всего было вакансий: {vacancies.count()}')
    count_append = 0

    for vacancy in vacancy_DF.to_dict('records'):
        if (vacancies.find({'vacancy_link':vacancy['vacancy_link']})).count() == 0:
            vacancies.insert_one(vacancy)
            count_append +=1
    print(f'Вакансий добавлено: {count_append}')



def insert_MongoDB(vacancy_DF, BDname, salary_from):
    db = client[BDname]
    vacancies = db.vacancies

    #необходимо использовать либо функцию insertAll
    #либо функцию insert_new
    #одновременно запускать их нет смысла

    insertAll(vacancy_DF, vacancies)

    find_gte_salary(vacancies, salary_from)

    #insert_new(vacancy_DF, vacancies)








