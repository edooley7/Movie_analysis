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

bad_titles = []

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


def money_to_int(moneystring):
    money = moneystring.replace('$', '').replace(',', '')
    return int(money)


def search_imbd(title):
    title = urllib.quote_plus(title)
    try:
        soup = souper("http://www.imdb.com/find?q=" + title + "&s=all")
        text = soup.select("#main .findList .findResult .result_text a")
        return_url = "http://www.imdb.com" + text[0]["href"]
    except:
        bad_titles.append(title)
        return_url = None
    return return_url


def get_budget_from_imdb(url):
    try:
        soup = souper(url)
        budget_text = soup.find('h4', text='Budget:').nextSibling
        budget = money_to_int(budget_text.strip())
    except:
        budget = 0
    return budget


def list_of_movie_pages():
    list_of_pages = []
    for i in range(2012, 2015):
        for j in range(1, 8):
            list_of_pages.append("http://www.boxofficemojo.com/yearly/chart/?page=" + str(j) + "&yr=" + str(i))
    return list_of_pages


def complete_movie_list(movie_pages):
    link_list = []
    for movie_url in movie_pages:
        soup = souper(movie_url)
        data = soup.findAll("div", id={"main"})
        for div in data:
            alinks = div.findAll('a')
            for l in alinks:
                if l.has_attr('href'):
                    if '/movies/?id=' in l['href']:
                        link_list.append("http://www.boxofficemojo.com" + l['href'])
    return link_list


def get_movie_values(soup, field_name):
    obj = soup.find(text=re.compile(field_name))
    if not obj:
        return None
    next_sibling = obj.findNextSibling()
    if next_sibling:
        return next_sibling.text
    else:
        return None


def budget_to_int(moneystring):
    if moneystring == "N/A":
        budget = 0
    else:
        budget = moneystring.replace('$', '').replace(',', '').replace('million', ' ')
    return float(budget)


def runtime_to_minutes(runtimestring):
    runtime = runtimestring.split()
    try:
        minutes = int(runtime[0])*60 + int(runtime[2])
        return minutes
    except:
        return None

def to_date(datestring):
    date = dateutil.parser.parse(datestring)
    return date

def get_director(soup):
    try:
        director = soup.find("a", {"href" : re.compile('view=Director&id=*')})
        director = director.text
        return director
    except:
        return None


movie_pages = list_of_movie_pages()
movie_links = complete_movie_list(movie_pages)

headers = ['title', 'production_budget', 'worldwide_gross',
           'domestic_gross', 'foreign_gross', 'genre', 'imdb_budget', 'distributor',
           'rating', 'runtime', 'release_date', 'director']

link_error = []
movie_data = []
for link in movie_links:
    try:
        souped_page = souper(link)

        title_string = souped_page.find('title').text
        title = title_string.split('(')[0].strip()

        imdb_url = search_imbd(title)
        imdb_budget = get_budget_from_imdb(imdb_url)

        genre = get_movie_values(souped_page, 'Genre:')

        director = get_director(souped_page)

        distributor = get_movie_values(souped_page, 'Distributor')

        rating = get_movie_values(souped_page, 'MPAA')

        raw_runtime = get_movie_values(souped_page, 'Runtime')
        runtime = runtime_to_minutes(raw_runtime)

        raw_release_date = get_movie_values(souped_page, 'Release Date')
        release_date = to_date(raw_release_date)

        raw_budget = get_movie_values(souped_page, 'Production Budget')
        budget = budget_to_int(raw_budget)

        domestic_text = souped_page.find(text=re.compile('Domestic'))
        b_tag = domestic_text.parent
        td_tag = b_tag.parent
        next_b_tag = b_tag.findNext('b')
        dtg = money_to_int(next_b_tag.contents[0])

        if souped_page.find(text=re.compile('Worldwide')) is None:
            worldwide = 0
        else:
            worldwide_text = souped_page.find(text=re.compile('Worldwide'))
            b_tag = worldwide_text.parent
            td_tag = b_tag.parent
            next_b_tag = b_tag.findNext('b')
            worldwide = money_to_int(next_b_tag.contents[0])

        if worldwide == 0:
            foreign = 0
        else:
            foreign = worldwide - dtg

        movie_dict = dict(zip(headers, [title, budget, worldwide, dtg, foreign, genre,
                                        imdb_budget, distributor, rating, runtime, release_date, director ]))
        movie_data.append(movie_dict)
        print "Success:", link
    except:
        link_error.append(link)
        print "Failed:", link

with open('TEST_movie_data.pkl', 'w') as picklefile:
    pickle.dump(movie_data, picklefile)

print len(bad_titles)
print 100 - (float(len(link_error)) / float(len(movie_links)) * 100), "% successful"
