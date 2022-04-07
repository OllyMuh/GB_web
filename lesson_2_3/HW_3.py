"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
только новые вакансии в вашу базу.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
(необходимо анализировать оба поля зарплаты).
"""
import re
import requests

from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pprint import pprint

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}

# search through hh.ru (big data work in Moscow) - 747 vacancies
# https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&text=Big+data&from=suggest_post
# https://hh.ru/search/vacancy?area=1&text=Big+data

# parameters
base_url = 'https://hh.ru'
area = '1'
text = 'Big+data'
items_on_page = 20

search_url = f'{base_url}/search/vacancy?area={area}&text={text}&items_on_page={items_on_page}'

client = MongoClient('localhost', 27017)
db = client["my_mongodb"]
vacancy_collection = db.vacancy_collection


def max_page():                         # function for finding max pagination page
    try:
        page = 0
        response = requests.get(search_url, headers=headers)
        dom = bs(response.text, 'html.parser')
        for item in dom.find_all('a', {'data-qa': 'pager-page'}):
            page = list(item.strings)[0].split(' ')[-1]
        return int(page)
    except ValueError:
        return 1


all_pages = max_page()
print(f'{all_pages} pages of pagination')


def collect(pages):                     # collecting data from the page and saving it in database "my_mongodb"
    compensation_min = 'None'
    compensation_max = 'None'
    compensation_currency = 'None'
    inserted = 0
    duplicates = 0

    for page in range(pages):
        url2 = f'{search_url}?page={page}'
        response = requests.get(url2, headers=headers)
        dom = bs(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
        for vacancy in vacancies:
            vacancy_data = {}
            vacancy_name = vacancy.find('a', {'class': 'bloko-link'}).getText()    # title of vacancy
            vacancy_link = vacancy.find('a', {'class': 'bloko-link'})['href']                       # vacancy link
            vacancy_id = re.search(r'\d+', vacancy_link)
            vacancy_compensation = vacancy.find('span',
                                                {'data-qa': 'vacancy-serp__vacancy-compensation'})  # vacancy salary
            if vacancy_compensation:
                vacancy_compensation = vacancy_compensation.text.replace('\u202f', '').split()
                if '-' in vacancy_compensation:
                    compensation_min = int(vacancy_compensation[0])
                    compensation_max = int(vacancy_compensation[2])
                    compensation_currency = vacancy_compensation[3]
                elif 'от' in vacancy_compensation:
                    compensation_min = int(vacancy_compensation[1])
                    compensation_max = 'None'
                    compensation_currency = vacancy_compensation[2]
                elif 'до' in vacancy_compensation:
                    compensation_min = 'None'
                    compensation_max = int(vacancy_compensation[1])
                    compensation_currency = vacancy_compensation[2]

            vacancy_data['name'] = vacancy_name
            vacancy_data['link'] = vacancy_link
            vacancy_data['min_salary'] = compensation_min
            vacancy_data['max_salary'] = compensation_max
            vacancy_data['currency'] = compensation_currency
            vacancy_data['site'] = base_url
            vacancy_data['_id'] = vacancy_id[0]

            try:
                vacancy_collection.insert_one(vacancy_data)
                inserted += 1
            except DuplicateKeyError:
                duplicates += 1
    return print(f'Inserted {inserted} new values, there have been {duplicates} duplicate values')


# data = collect(all_pages)
# vacancy_base.drop()


def show_higher(salary):
    req = {'$or': [{'max_salary': {'$gte': salary}}, {'min_salary': {'$lte': salary}}]}
    result = vacancy_collection.find(req)
    for doc in result:
        pprint(doc)

# show_higher(400000)

