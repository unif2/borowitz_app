from bs4 import BeautifulSoup
from time import sleep
import json
import sys
from urllib.request import urlopen
import string

sys.setrecursionlimit(100000)

# Load the JSON with past article data
with open('final_borowitz.json', 'r') as fp:
    past_articles = json.load(fp)
fp.close()

# Most recent article is the one at the top of the list.  Article link is the third entry.
most_recent_article_url = past_articles[0][2]

base_url_page = 'https://www.newyorker.com/humor/borowitz-report/page/'

# This block of code scrapes the unique URL portion specific to each article on each page and stores them in links and
# stops when it scrapes a link that's already in the json file

def link_scraper(base_url_page):
    print('Scraping all new article link addresses.')
    i=1
    links = []
    full_link = ''
    while full_link != most_recent_article_url:
        sleep(0.1)
        page = urlopen(base_url_page+str(i))
        soup = BeautifulSoup(page, "html.parser")
        #stuff = soup.find_all("a", attrs={"class":"Link__link___3dWao  "})
        stuff2 = soup.find_all('li', attrs={"class":"River__riverItem___3huWr"})
        things = []
        for blah in stuff2:
            if blah.find_next("h4"):
                things.append(blah.find_all("a", attrs={"class":"Link__link___3dWao"}))

        for thing in things:
            link = thing[0].findNext({"a":"href"}).get('href')
            full_link = 'https://www.newyorker.com'+link
            if full_link == most_recent_article_url:
                if links:
                    print('Done. %d new links found.' %len(links))
                else:
                    print('Done. No new links found.')
                return links
            else:
                links.append(link)
        full_link = 'https://www.newyorker.com'+links[-1]
        i += 1

# Clean up the article text for each article

def article_clean(article):
    article = article.replace('\xa0', u' ')
    article = article.replace("Get news satire from The Borowitz Report delivered to your inbox.", "")
    article = article.replace("Get the Borowitz Report delivered to your inbox.", "")
    article = article.replace("Get The Borowitz Report delivered to your inbox.", "")
    article = article.replace("(The Borowitz Report)", "")
    article = article.replace("News Satire from The Borowitz Report", "")
    article = article.replace("Satire from The Borowitz Report", "")
    article = article.replace("This post is news satire from The Borowitz Report.", "")
    article = article.replace("News satire from The Borowitz Report.", "")
    article = article.replace("Andy Borowitz will be doing a free show at Rutgers University on Monday, October 29, at 7 P.M. To register for tickets, click here.    Photograph by Lauren Lancaster.", "")
    article = article.replace("Andy Borowitz is doing a show to benefit public radio.","")
    article = article.replace("Tickets for Andy Borowitz's next live show are now on sale.", "")
    article = article.replace("(Satire from The Borowitz Report)", "")
    article = article.replace("Illustration by Andy Borowitz.", "")
    article = article.replace("Andy Borowitz will be doing two shows at next month's New Yorker Festival: Friday, October 5th, with the storytelling group The Moth, and Saturday, October 6th, with Sarah Silverman. Ticket information here.", "")
    article = article.replace("A small number of tickets have just been released for Andy Borowitz's New Yorker Festival show this Friday night in New York City. Buy tickets here.", "")
    article = article.replace("(Satire from The Borowitz Report)", "")
    article = article.replace("Tickets for Andy Borowitz's next live show are now on sale.  Photograph by Alex Wong/Getty.", "")
    article = article.replace("Tickets for Andy Borowitz's next live show are now on sale.      Illustration by Tom Bachtell.", "")
    article = article.replace("Andy Borowitz will be doing two shows at next month's New Yorker Festival: Friday, October 5th, with the storytelling group The Moth, and Saturday, October 6th, with Sarah Silverman. Ticket information here.    Photograph by Tony Avelar/Bloomberg/Getty Images.", "")
    article = article.replace("(The Borowitz Report)", "")
    article = article.replace("Tickets for Andy Borowitz's next live show are now on sale.  Photograph by Chris Maddaloni/CQ Roll Call.", "")
    article = article.replace("(Satire from The Borowitz Report)", "")
    article = article.replace('"', " ").replace("'",'').replace('“',' ').replace('”',' ').replace("’",'').replace('-',' ').replace('--',' ').replace('—',' ').replace('…',' ')
    article = "".join((char.lower() for char in article if char not in string.punctuation))
    return article
        
# This function scrapes the article text, article title, and article date for an article
def text_scraper(link):
    url = 'https://www.newyorker.com'+link
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    article_text = soup.find("div", attrs={"id":"articleBody"}).text
    article_text = article_clean(article_text)
    title = soup.find('title').text
    date = soup.find('p', attrs={'class':"ArticleTimestamp__timestamp___1klks "}).text
    return [title, date, url, article_text]

# Store what text_scraper returns in d
d = []

# If a hiccup occurs (i.e., if a request was blocked), store the link that caused it in not_scraped
not_scraped = []

links = link_scraper(base_url_page)

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

# If there are new articles, prepend the data to past_articles and write everything to json file
if d:
    d.extend(past_articles)
    with open('/home/velocci/mysite/final_borowitz.json', 'w') as fp:
        json.dump(d, fp)
    fp.close
else:
    print('No new articles.')