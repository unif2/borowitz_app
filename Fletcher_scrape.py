from bs4 import BeautifulSoup
from time import sleep
import json
import sys
from urllib.request import urlopen

sys.setrecursionlimit(100000)

num_pages = 86
base_url = 'https://www.newyorker.com/humor/borowitz-report'
base_url_page = 'https://www.newyorker.com/humor/borowitz-report/page/'
urls = [base_url_page + str(i) for i in range(2,num_pages+1)]
all_urls = [base_url]
all_urls.extend(urls)

links = []
print('Scraping all article link addresses')
for url in all_urls:
    sleep(0.1)
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    stuff = soup.find_all("a", attrs={"class":"Link__link___3dWao  "})
    stuff2 = soup.find_all('li', attrs={"class":"River__riverItem___3huWr"})
    things = []
    for blah in stuff2:
        if blah.find_next("h4"):
            things.append(blah.find_all("a", attrs={"class":"Link__link___3dWao"}))

    for thing in things:
        links.append(thing[0].findNext({"a":"href"}).get('href'))

print('Done.')

d = []

for link in links:
    print('Scraping stuff from link %s' %link)
    sleep(2)
    page = urlopen(link)
    soup = BeautifulSoup(page, "html.parser")
    article_text = soup.find("div", attrs={"id":"articleBody"}).text
    title = soup.find('title').text
    date = soup.find('p', attrs={'class':"ArticleTimestamp__timestamp___1klks "}).text
    d.append([title, date, link, article_text])

with open('final_borowitz.json', 'w') as fp:
	json.dump(d, fp)