from __future__ import print_function, division
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
import pickle
import html5lib
import re
import sys
import collections

sys.setrecursionlimit(100000)

base_url = 'http://www.newyorker.com/humor/borowitz-report'
base_url_page = 'http://www.newyorker.com/humor/borowitz-report/page/'
urls = [base_url_page + str(i) for i in range(2,71)]
all_urls = [base_url]
all_urls.extend(urls)

links = []
print('Scraping all urls')
for url in all_urls:
	sleep(0.1)
	soup = BeautifulSoup(requests.get(url).text, 'html5lib')
	foo_url = soup.findAll('h2')
	for x in foo_url:
		links.append(x.findNext({"a":"href"}).get('href'))

print('Done scraping all urls')
d = dict()

for link in links:
	print('Scraping stuff from link %s' %link)
	sleep(0.1)
	soup = BeautifulSoup(requests.get(link).text, 'html5lib')
	print('Scraping the text from %s' %link)
	foo_text = ' '.join(p.text for p in soup.findAll("p") if p.has_attr("word_count"))
	print('Scraping the title from %s' %link)
	x = soup.findAll('h1')
	for p in x:
		if p.has_attr("itemprop"):
			foo_title = p.text
	#foo_title = soup.findAll('h1', {"class" : "title"}).text
	print('Scraping the date from %s' %link)

	t = soup.findAll('time')
	for y in t:
		if y.has_attr('content'):
			foo_date = y.attrs['content']

	#foo_date = t.attrs['content']
	d[(foo_title, foo_date, link)] = foo_text

#d.to_pickle('borowitz.pkl')
with open('final_borowitz.pickle', 'wb') as handle:
	pickle.dump(d, handle)
