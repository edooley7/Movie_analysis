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

def get_director(soup):
    director = soup.find("a", {"href" : re.compile('view=Director&id=*')})
    director = director.text
    return director

print get_director(souper("http://www.boxofficemojo.com/movies/?id=americansniper.htm"))