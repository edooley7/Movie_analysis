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


# Visits pages with a random interval, sleeps for 3 sec if get request not successful
def get_page(url):
    sleep(randint(0, 1))
    response = requests.get(url)
    if int(response.status_code) != 200:
        time.sleep(3)
        response = requests.get(url)
        print "Retried. Got status code:", response.status_code
        return response.text
    else:
        return response.text


# Gets page and turns it into soup
def souper(url):
    page = get_page(url)
    soup = BeautifulSoup(page)
    return soup


# Converts money string in gross figures to int
def money_to_int(moneystring):
    money = moneystring.replace('$', '').replace(',', '')
    return int(money)


# Searches IMDB for box office mojo title and returns link for first result
# Adds title to bad_titles list if it can't find title
def search_imdb(title):
    title = urllib.quote_plus(title)
    try:
        soup = souper("http://www.imdb.com/find?q=" + title + "&s=all")
        text = soup.select("#main .findList .findResult .result_text a")
        return_url = "http://www.imdb.com" + text[0]["href"]
    except:
        bad_titles.append(title)
        return_url = None
    return return_url


# Finds budget on IMDB page
def get_budget_from_imdb(url):
    try:
        soup = souper(url)
        budget_text = soup.find('h4', text='Budget:').nextSibling
        budget = money_to_int(budget_text.strip())
    except:
        budget = None
    return budget

def get_director_from_imdb(url):
    soup = souper(url)
    text = soup.select('span', {'class': 'itemprop'})
    director = text[0]["href"]
    return director

# Generates list of pages to search for movie links on
def list_of_movie_pages():
    list_of_pages = []
    for i in range(2012, 2013):
        for j in range(1, 2):
            list_of_pages.append("http://www.boxofficemojo.com/yearly/chart/?page=" + str(j) + "&yr=" + str(i))
    return list_of_pages


# Creates list of movie pages
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


# Gets value for regex search of field name
def get_movie_values(soup, field_name):
    obj = soup.find(text=re.compile(field_name))
    if not obj:
        return None
    next_sibling = obj.findNextSibling()
    if next_sibling:
        return next_sibling.text
    else:
        return None


# Converts Mojo budget to float
def budget_to_int(moneystring):
    if moneystring == "N/A":
        budget_float = None
    else:
        budget_float = moneystring.replace('$', '').replace(',', '').replace('million', ' ')
    return float(budget_float)


# Converts Mojo runtime to minutes
def runtime_to_minutes(runtimestring):
    runtime = runtimestring.split()
    try:
        minutes = int(runtime[0]) * 60 + int(runtime[2])
        return minutes
    except:
        return None


# Converts Mojo dates to parsable datetime objects
def to_date(datestring):
    date = dateutil.parser.parse(datestring)
    return date


def get_widest_release(soup):
    widest  = soup.find('td', text='Widest Release:').nextSibling
    return widest


headers = ['title', 'production_budget', 'worldwide_gross',
           'domestic_gross', 'foreign_gross', 'genre', 'imdb_budget', 'distributor',
           'rating', 'runtime', 'release_date', 'widest_release', 'director']

bad_titles = []
link_error = []
movie_data = []
test_url = ["http://www.boxofficemojo.com/movies/?id=americansniper.htm"]
movie_pages = list_of_movie_pages()
movie_links = complete_movie_list(movie_pages)

def create_movie_data_dict(movie_links):
    for link in movie_links:
        try:
            print "Tried:", link

            souped_page = souper(link)

            title_string = souped_page.find('title').text
            title = title_string.split('(')[0].strip()

            imdb_url = search_imdb(title)
            imdb_budget = get_budget_from_imdb(imdb_url)

            genre = get_movie_values(souped_page, 'Genre:')

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
            next_b_tag = b_tag.findNext('b')
            dtg = money_to_int(next_b_tag.contents[0])

            if souped_page.find(text=re.compile('Worldwide')) is None:
                worldwide = None
            else:
                worldwide_text = souped_page.find(text=re.compile('Worldwide'))
                b_tag = worldwide_text.parent
                next_b_tag = b_tag.findNext('b')
                worldwide = money_to_int(next_b_tag.contents[0])

            if worldwide == None:
                foreign = None
            else:
                foreign = worldwide - dtg

            movie_dict = dict(zip(headers, [title, budget, worldwide, dtg, foreign, genre,
                                            imdb_budget, distributor, rating, runtime, release_date,
                                            widest_release, director]))
            movie_data.append(movie_dict)
        except:
            link_error.append(link)

create_movie_data_dict(movie_links)

with open('test_movie_data.pkl', 'w') as picklefile:
    pickle.dump(movie_data, picklefile)

print len(bad_titles), "box office mojo titles were not found on IMDB"
print 100 - (float(len(link_error)) / float(len(movie_links)) * 100), "% successful"