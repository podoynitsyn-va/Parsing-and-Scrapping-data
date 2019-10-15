#Урок 1

#1. Посмотреть документацию к API GitHub,
#разобраться как вывести список репозиториев для конкретного пользователя,
#сохранить JSON-вывод в файле *.json

import requests
import json

username = input('Введите логин пользователя GitHub: ')
link = f'https://api.github.com/users/{username}/repos'

request = requests.get(link)
if request.ok:
    repos_info = json.loads(request.text)

    with open(f'{username}_repos_data.json','w') as repos_file:
        json.dump(repos_info, repos_file)

    print(f'Для пользователя {username} существуют следующие репозитории:')
    for repos in repos_info:
        print(repos.get('name'))
else:
    print('Неверно введён логин пользователя GitHub!')


#2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию через curl, Postman, Python.
# Ответ сервера записать в файл (приложить скриншот для Postman и curl)

#возьмём пример из вебинара:
link = 'https://postman-echo.com/basic-auth'
headers = {'Authorization':'Basic cG9zdG1hbjpwYXNzd29yZA=='}
request = requests.get(link, headers=headers)
answer = request.text
print(f'Ответ {link}: {answer}')
with open('answer_postman-echo.com.json', 'w') as answer_file:
    json.dump(answer, answer_file)

#Попробуем получить данные об организации GEEKBRAINS из ЕГРЮЛ, используя API ФНС:

#ИНН организации:
INN = '7726381870'

#ОГРН организации:
OGRN = '1167746654569'

#API ключ разработчика:
API_key = '2517d52f21501aca5aaf80066461fad0e55dfdca'

#адрес сервиса:
link = 'https://api-fns.ru/api/egr'

request = requests.get(f'{link}?req={INN}&key={API_key}')
answer = json.loads(request.text)
firm_info = answer.get('items')[0].get('ЮЛ')
with open('geekbrains_data.json', 'w') as answer_file:
    json.dump(answer, answer_file)

#Получим, для примера, данные об учредителях:
for founder in firm_info.get('Учредители'):
    print(founder.get('УчрФЛ'))

