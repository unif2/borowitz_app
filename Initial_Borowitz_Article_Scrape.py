from bs4 import BeautifulSoup
from time import sleep
import json
import sys
from urllib.request import urlopen

sys.setrecursionlimit(100000)

# Current number of pages of Borowitz Reports
num_pages = 93

# First page
base_url = 'https://www.newyorker.com/humor/borowitz-report'

# All subsequent pages
base_url_page = 'https://www.newyorker.com/humor/borowitz-report/page/'
urls = [base_url_page + str(i) for i in range(2,num_pages+1)]

# Here is our list of page URLs
page_urls = [base_url]
page_urls.extend(urls)

# This block of code scrapes the unique URL portion specific to each article on each page and stores them in links
links = []
print('Scraping all article link addresses')
for url in page_urls:
    sleep(0.1)
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    #stuff = soup.find_all("a", attrs={"class":"Link__link___3dWao  "})
    stuff2 = soup.find_all('li', attrs={"class":"River__riverItem___3huWr"})
    things = []
    for blah in stuff2:
        if blah.find_next("h4"):
            things.append(blah.find_all("a", attrs={"class":"Link__link___3dWao"}))

    for thing in things:
        links.append(thing[0].findNext({"a":"href"}).get('href'))

print('Done.')

# This function scrapes the article text, article title, and article date for an article
def text_scraper(link):
    url = 'https://www.newyorker.com'+link
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    article_text = soup.find("div", attrs={"id":"articleBody"}).text
    title = soup.find('title').text
    date = soup.find('p', attrs={'class':"ArticleTimestamp__timestamp___1klks "}).text
    return [title, date, url, article_text]

# Store what text_scraper returns in d
d = []

# If a hiccup occurs (i.e., if a request was blocked), store the link that caused it in not_scraped
not_scraped = []

for link in links:
    print('Scraping stuff from link %s' %link)
    sleep(2)
    try:
        d.append(text_scraper(link))
    except:
        not_scraped.append(link)
        continue

# If hiccups occurred, go back and try to scrape again
if not_scraped:
    for link in not_scraped:
        print('Scraping stuff from link %s' %link)
        sleep(2)
        d.append(text_scraper(link))

# Clean up the article text for each article
for article in d:
    article[3] = article[3].replace('\xa0', u' ')
    article[3] = article[3].replace("Get news satire from The Borowitz Report delivered to your inbox.", "")
    article[3] = article[3].replace("Get the Borowitz Report delivered to your inbox.", "")
    article[3] = article[3].replace("Get The Borowitz Report delivered to your inbox.", "")
    article[3] = article[3].replace("(The Borowitz Report)", "")
    article[3] = article[3].replace("News Satire from The Borowitz Report", "")
    article[3] = article[3].replace("Satire from The Borowitz Report", "")
    article[3] = article[3].replace("This post is news satire from The Borowitz Report.", "")
    article[3] = article[3].replace("News satire from The Borowitz Report.", "")
    article[3] = article[3].replace("Andy Borowitz will be doing a free show at Rutgers University on Monday, October 29, at 7 P.M. To register for tickets, click here.    Photograph by Lauren Lancaster.", "")
    article[3] = article[3].replace("Andy Borowitz is doing a show to benefit public radio.","")
    article[3] = article[3].replace("Tickets for Andy Borowitz's next live show are now on sale.", "")
    article[3] = article[3].replace("(Satire from The Borowitz Report)", "")
    article[3] = article[3].replace("Illustration by Andy Borowitz.", "")
    article[3] = article[3].replace("Andy Borowitz will be doing two shows at next month's New Yorker Festival: Friday, October 5th, with the storytelling group The Moth, and Saturday, October 6th, with Sarah Silverman. Ticket information here.", "")
    article[3] = article[3].replace("A small number of tickets have just been released for Andy Borowitz's New Yorker Festival show this Friday night in New York City. Buy tickets here.", "")
    article[3] = article[3].replace("(Satire from The Borowitz Report)", "")
    article[3] = article[3].replace("Tickets for Andy Borowitz's next live show are now on sale.  Photograph by Alex Wong/Getty.", "")
    article[3] = article[3].replace("Tickets for Andy Borowitz's next live show are now on sale.      Illustration by Tom Bachtell.", "")
    article[3] = article[3].replace("Andy Borowitz will be doing two shows at next month's New Yorker Festival: Friday, October 5th, with the storytelling group The Moth, and Saturday, October 6th, with Sarah Silverman. Ticket information here.    Photograph by Tony Avelar/Bloomberg/Getty Images.", "")
    article[3] = article[3].replace("(The Borowitz Report)", "")
    article[3] = article[3].replace("Tickets for Andy Borowitz's next live show are now on sale.  Photograph by Chris Maddaloni/CQ Roll Call.", "")
    article[3] = article[3].replace("(Satire from The Borowitz Report)", "")
    article[3] = article[3].replace('"', "").replace("'",'').replace('“','').replace('”','').replace("’",'').replace('-',' ').replace('--',' ').replace('—',' ').replace('…',' ')

with open('final_borowitz.json', 'w') as fp:
    json.dump(d, fp)

fp.close()