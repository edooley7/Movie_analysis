__author__ = 'erindooley'

import requests
from bs4 import BeautifulSoup
import re
import dateutil.parser
import pandas as pd

url = 'http://www.boxofficemojo.com/movies/?id=americansniper.htm'


#Gets all the text on a page and converts it to BS object
response = requests.get(url)
page = response.text
soup = BeautifulSoup(page)

def get_movie_values(soup, field_name):
    obj = soup.find(text=re.compile(field_name))
    if not obj:
        return None
    next_sibling = obj.findNextSibling()
    if next_sibling:
        return next_sibling.text
    else:
        return None


def money_to_int(moneystring):
    moneystring = moneystring.replace('$', '').replace(',', '')
    return int(moneystring)

def budget_to_int(moneystring):
    moneystring = moneystring.replace('$', '').replace(',', '').replace('million',' ')
    return float(moneystring)

title_string = soup.find('title').text
title = title_string.split('(')[0].strip()
print "Title:", title

raw_budget = get_movie_values(soup,'Production Budget')
budget = budget_to_int(raw_budget)*1000000
print "Budget:", budget

raw_dtg = get_movie_values(soup,'Domestic Total')
dtg = money_to_int(raw_dtg)
print "Domestic Gross:", dtg

dom_roi = dtg/budget
print "Domestic ROI", dom_roi

domestic_total_regex = re.compile('Worldwide')
soup.find(text=domestic_total_regex)
worldwide_text = soup.find(text=re.compile('Worldwide'))

b_tag = worldwide_text.parent
td_tag = b_tag.parent
next_b_tag = b_tag.findNext('b')
worldwide = money_to_int(next_b_tag.contents[0])
print "Worldwide:", worldwide

wor_roi = worldwide/budget
print "Worldwide ROI", wor_roi

foreign = worldwide - dtg
print "Foreign:", foreign

for_roi = foreign/budget
print "Foreign ROI:", for_roi

headers = ['title', 'production budget', 'worldwide gross',
           'domestic gross', 'foreign gross', 'world roi',
           'domestic roi', 'foreign roi']

def list_of_movie_pages():
    list_of_pages = []
    for i in range(2012, 2014):
        for j in range(1,6):
            list_of_pages.append("http://www.boxofficemojo.com/yearly/chart/?page="+str(j)+"&yr="+ str(i))
    return list_of_pages

movie_pages = list_of_movie_pages()

complete_movie_list = []
for pages in movie_pages:
    movie_url = pages
    response = requests.get(movie_url)
    page = response.text
    soup = BeautifulSoup(page)
    list_of_movies = soup.findAll('a', href = re.compile('movies'))
    complete_movie_list.append(list_of_movies)
print complete_movie_list