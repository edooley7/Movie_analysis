__author__ = 'erindooley'


import requests
from bs4 import BeautifulSoup
import re
import pickle
import time
import urllib
import dateutil.parser
from time import sleep
from random import randint


def get_page(url):
    sleep(randint(0,1))
    response = requests.get(url)
    if int(response.status_code) != 200:
        time.sleep(3)
        response = requests.get(url)
        print "Retried. Got status code:", response.status_code
        return response.text
    else:
        return response.text

def souper(url):
    page = get_page(url)
    soup = BeautifulSoup(page)
    return soup


def list_of_director_pages():
    list_of_director_pages = []
    for i in range(1, 18):
        list_of_director_pages.append("http://www.boxofficemojo.com/people/?view=Director&pagenum="
                                      + str(i) + "&sort=sumgross&order=DESC&&p=.htm")
    return list_of_director_pages

director_pages = list_of_director_pages()

def complete_movie_list(director_pages):
    link_list = []
    for director_url in director_pages:
        soup = souper(director_url)
        dir_hrefs = soup.findAll("a", {"href" : re.compile('view=Director&id=*')})
        for link in dir_hrefs:
            link_href = "http://www.boxofficemojo.com/people/" + link['href']
            if link_href not in link_list:
                link_list.append(link_href)
    return link_list


director_page_list = complete_movie_list(director_pages)

def money_to_int(moneystring):
    money = moneystring.replace('$', '').replace(',', '')
    return int(money)


headers = ['director', 'lifetime_gross', 'lifetime_films']
director_data = []
bad_pages = []
for page in director_page_list:
    try:
        print "Tried:", page
        soup = souper(page)
        director = soup.find('h1').text
        raw_lifetime = soup.find(text=re.compile("Lifetime Gross Total"))
        lifetime_gross = money_to_int(raw_lifetime.split(':')[1].strip())
        lifetime_split = raw_lifetime.replace('(', '').replace(')','').replace(':', '').split()
        lifetime_films = lifetime_split[3].strip()
        director_dict = dict(zip(headers, [director, lifetime_gross, lifetime_films ]))
        director_data.append(director_dict)
    except:
        bad_pages.append(page)
        print "Failed", page

print len(director_data)

with open('director_movie_data.pkl', 'w') as picklefile:
    pickle.dump(director_data, picklefile)

