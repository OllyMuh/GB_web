"""
pip install lxml
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости. 
для парсинга использовать XPath. Структура данных должна содержать:
            название источника;
            наименование новости;
            ссылку на новость;
            дата публикации.
Сложить собранные новости в БД
Минимум один сайт, максимум - все три
"""

import requests
import re

from lxml import html
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

url = 'https://news.mail.ru/'
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}  # chrome://version/
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)

client = MongoClient('localhost', 27017)
db = client['news_db']
news_collection = db.news_collection

news_links = dom.xpath("//div/a[contains(@class, 'js-topnews')]/@href")
news_links.extend(dom.xpath("//li[@class='list__item']/a/@href"))

for link in news_links:
    news_info = {}
    inner_response = requests.get(link, headers=headers)
    inner_dom = html.fromstring(inner_response.text)
    news_id = re.search(r'\d+', link)
    source = inner_dom.xpath("//div[contains(@class, 'multi')]//span[@class='link__text']/text()")
    title = inner_dom.xpath('//h1/text()')
    published = inner_dom.xpath("//div[contains(@class, 'multi')]//span[contains(@class, 'js-ago')]/@datetime")
    news_info['_id'] = news_id[0]
    news_info['link'] = link
    news_info['source'] = source[0]
    news_info['title'] = title[0]
    news_info['published'] = published[0][:10]

    try:
        news_collection.insert_one(news_info)
    except DuplicateKeyError:
        print('Already exists in the base')


# for doc in news_collection.find({}):
#     pprint(doc)

# news_collection.drop()