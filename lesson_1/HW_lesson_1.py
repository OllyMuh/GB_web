"""
1. Посмотреть документацию к API GitHub, разобраться как вывести список наименований репозиториев для конкретного
пользователя, сохранить JSON-вывод в файле *.json.
"""

import requests
from pprint import pprint
import json

user = 'OllyMuh'
url = 'https://api.github.com/users/'+user+'/repos'

response = requests.get(url)
j_data = response.json()
# pprint(j_data)

# вывод всех публичных репозиториев
[print(f"- {items['name']}") for items in j_data]

# список репозиториев
repos = [[items['name'] for items in j_data]]
print(repos)

# сохранение в json файл
with open('data.txt', 'w') as file:
    json.dump(j_data, file)