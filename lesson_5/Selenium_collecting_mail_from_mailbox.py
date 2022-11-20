"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о
письмах в базу данных (
                        от кого,
                        дата отправки,
                        тема письма,
                        текст письма полный)
"""
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from secret import login_mail, password_mail

chrome_options = Options()

chrome_options.add_argument('--no-sandbox')
s = Service('/home/oem/GB_web/lesson_5/chromedriver')
driver = webdriver.Chrome(service=s, chrome_options=chrome_options)

driver.get('https://mail.ru')
enter = driver.find_element(By.XPATH, "//button[contains(@data-testid, 'enter-mail-primary')]")
enter.send_keys(Keys.ENTER)

wait = WebDriverWait(driver, 10)

# enter login - my post
iframe = driver.find_element(By.XPATH, '//iframe[@class="ag-popup__frame__layout__iframe"]')
driver.switch_to.frame(iframe)
login = driver.find_element(By.NAME, 'username')
login.send_keys(login_mail)
login.send_keys(Keys.ENTER)

# enter password
passwd = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'password')))
passwd.send_keys(password_mail)
passwd.send_keys(Keys.ENTER)

# make the list of links
links = []
xpath = "//a[contains(@href, '/inbox/0:')]"
wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
last_id = None

while True:
    letters = driver.find_elements(By.XPATH, xpath)
    last = letters[-1].get_attribute('href')
    if last_id == last:
        break

    for letter in letters:
        links.append(letter.get_attribute('href').split('?')[0])

    last_id = last

    actions = ActionChains(driver)
    actions.move_to_element(letters[-1]).perform()
    sleep(10)

links = list(set(links))

# making the base of letters
client = MongoClient('localhost', 27017)
db = client['letters_db']
letter_collection = db.letter_collection

for link in links:
    letters = {}
    driver.get(link)
    topic = wait.until(EC.presence_of_element_located((By.XPATH, '//h2[contains(@class, "subject")]'))).text
    sender = wait.until(EC.presence_of_element_located((By.XPATH,
                                                        '//div[@class="letter__author"]/span'))).get_attribute('title')
    sent = wait.until(EC.presence_of_element_located((By.XPATH,
                                                     "//div[@class='letter__date']"))).text
    letter_text = wait.until((EC.presence_of_element_located((By.XPATH,
                                                              "//div[@class='letter__body']")))).text
    letters['_id'] = link
    letters['sender'] = sender
    letters['sent'] = sent
    letters['text'] = letter_text.replace('\n', ' ')

    try:
        letter_collection.insert_one(letters)
    except DuplicateKeyError:
        print('Already in the base')

for doc in letter_collection.find({}):
    pprint(doc)






