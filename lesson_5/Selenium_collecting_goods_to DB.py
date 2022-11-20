"""
2) Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает данные в БД.
Сайт можно выбрать и свой. Главный критерий выбора: динамически загружаемые товары

https://www.21vek.by/
"""

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--start-maximized")
s = Service('/home/oem/GB_web/lesson_5/chromedriver')
driver = webdriver.Chrome(service=s, chrome_options=chrome_options)

url = 'https://www.21vek.by/special_offers/promo.html?discountTypes=discount&discountRange=50'
driver.get(url)
wait = WebDriverWait(driver, 10)

# opening 2 pages...
page = 1
while page <= 2:
    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="styles_reactButton__2olKd style_loadMoreButtonNew__QUAYt"]')))
        button.click()
        page += 1
    except exceptions.TimeoutException:
        print('Больше не на что нажимать')
        break

# making the base
client = MongoClient('localhost', 27017)
db = client['goods_db']
goods_collection = db.goods_collection

# collecting goods data to the base
goods = driver.find_elements(By.XPATH, "//div[@class='style_rootProduct__UjCzM style_product__irNOY']")

for good in goods:
    good_elem = {}
    title = good.find_element_by_xpath('.//div[@class="style_nameProduct__1NxDv"]/a').text
    price = good.find_element_by_xpath('.//div[@class="style_currentPrice__2ztp8"]').text
    prod_id = good.find_element_by_xpath('.//div[@class="style_code__Cz60m style_code__1NUe5"]').text
    discount = good.find_element_by_xpath('//span[@class="style_promoDiscount__2Z5dm"]').text

    good_elem['_id'] = prod_id
    good_elem['title'] = title
    good_elem['price'] = float(price.replace(',', '.').split()[0])
    good_elem['discount'] = discount

    try:
        goods_collection.insert_one(good_elem)
    except DuplicateKeyError:
        print('Где-то я это уже видела')

# result
for doc in goods_collection.find({}):
    pprint(doc)


