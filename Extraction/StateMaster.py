import pandas as pd
import requests
import json
import prettytable
import bs4
from bs4 import BeautifulSoup

base_site = 'http://www.statemaster.com'
website = 'http://www.statemaster.com/statistics'
response = requests.get(website)
print(response.text)
statemaster_website = BeautifulSoup(response.text, features="html.parser")
categories: list[bs4.Tag] = list(filter(lambda x: 'cat' in str(x), statemaster_website.find_all('a')))
print(categories)
categories_dict = {category.text: category.attrs['href'] for category in categories}
print(categories_dict)

with open('..\\Features\\Original StateMaster Features.txt', 'w+') as writer:
    for category in categories:
        cat_website = base_site + category.attrs['href'] + '&all=1'
        cat_response = requests.get(cat_website)
        statemaster_cat_website = BeautifulSoup(cat_response.text, features="html.parser")
        tbody: bs4.Tag = statemaster_cat_website.find_all('table', attrs={'class': 'body', 'width': '100%'})[0]
        rows: list[bs4.Tag] = tbody.find_all('a')
        # print(rows, len(rows))
        category.attrs['fields'] = list(filter(lambda x: 'map' not in x and 'pie' not in x, [row.text for row in rows]))
        print(category.text, len(category.attrs['fields']), category.attrs['fields'])
        writer.write(str(category.text) + '\n')
        for row in category.attrs['fields']:
            writer.write('\t' + str(row) + '\n')
