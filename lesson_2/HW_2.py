"""
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
(также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
Сохраните в json либо csv.
"""

import pandas as pd
import requests

from bs4 import BeautifulSoup as bs
from pprint import pprint

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}

# search through hh.ru (remote work in Moscow)
# https://https://hh.ru/search/vacancy?area=1005&fromSearchLine=true&text=remote

# parameters
base_url = 'https://hh.ru'
area = 'Moscow'
text = 'big+data'
items_on_page = 20

search_url = f'{base_url}/search/vacancy?area={area}&&fromSearchLine=true&text={text}&items_on_page={items_on_page}'

# params = {'area': 'Moscow',
#           'text': 'big+data',
#           'items_on_page': 20}    -- не пригодилось


# function for finding max pagination page
def max_page():
    try:
        page = 0
        response = requests.get(search_url, headers=headers)
        dom = bs(response.text, 'html.parser')
        for item in dom.find_all('a', {'data-qa': 'pager-page'}):
            page = list(item.strings)[0].split(' ')[-1]
        return int(page)
    except:
        return 1


all_pages = max_page()
# print(all_pages)


# collecting data from the page
def collect(pages):
    vacancy_list = []
    compensation_min = 'None'
    compensation_max = 'None'
    compensation_currency = 'None'

    for page in range(pages):
        url2 = f'{search_url}?page={page}'
        response = requests.get(url2, headers=headers)
        dom = bs(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
        for vacancy in vacancies:
            vacancy_data = {}
# title of vacancy
            vacancy_name = vacancy.find('span', {'class': 'resume-search-item__name'}).getText()
            # vacancy link
            vacancy_link = vacancy.find('a', {'class': 'bloko-link'})['href']
# vacancy salary
            vacancy_compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            # vacancy_compensation_data = {'min': '',  # minimum
            #                              'max': '',  # maximum
            #                              'currency': ''}  # currency              -- для другой формы сбора данных з/п
            if vacancy_compensation:
                vacancy_compensation = vacancy_compensation.text.replace('\u202f', '').split()
                if '-' in vacancy_compensation:
                    # vacancy_compensation_data['min'] = int(vacancy_compensation[0])
                    compensation_min = int(vacancy_compensation[0])
                    # vacancy_compensation_data['max'] = int(vacancy_compensation[2])
                    compensation_max = int(vacancy_compensation[2])
                    # vacancy_compensation_data['currency'] = vacancy_compensation[3]
                    compensation_currency = vacancy_compensation[3]
                elif 'от' in vacancy_compensation:
                    # vacancy_compensation_data['min'] = int(vacancy_compensation[1])
                    compensation_min = int(vacancy_compensation[1])
                    # vacancy_compensation_data['max'] = 'None'
                    compensation_max = 'None'
                    # vacancy_compensation_data['currency'] = vacancy_compensation[2]
                    compensation_currency = vacancy_compensation[2]
                elif 'до' in vacancy_compensation:
                    # vacancy_compensation_data['min'] = 'None'
                    compensation_min = 'None'
                    # vacancy_compensation_data['max'] = int(vacancy_compensation[1])
                    compensation_max = int(vacancy_compensation[1])
                    # vacancy_compensation_data['currency'] = vacancy_compensation[2]
                    compensation_currency = vacancy_compensation[2]
            # else:
                # vacancy_compensation_data['min'] = 'None'
                # vacancy_compensation_data['max'] = 'None'
                # vacancy_compensation_data['currency'] = 'None'

            # create vacancy dictionary
            vacancy_data['name'] = vacancy_name
            vacancy_data['link'] = vacancy_link
            # vacancy_data['vacancy_compensation'] = vacancy_compensation_data
            vacancy_data['min_salary'] = compensation_min
            vacancy_data['max_salary'] = compensation_max
            vacancy_data['currency'] = compensation_currency
            vacancy_data['site'] = base_url

            # collect dictionaries in a list
            vacancy_list.append(vacancy_data)

    return vacancy_list


data = collect(all_pages)


# create dataframe from list of dictionaries
df = pd.DataFrame.from_dict(data, orient='columns')
# print(df.head())

df.to_csv('vacancy_base.csv')