from flask import Flask
from flask import request
from flask import render_template

import pickle
import numpy as np
import urllib2
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from gensim import corpora, models, similarities, matutils
from sklearn.decomposition import NMF
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib
from cookielib import CookieJar
import webbrowser

stop_words = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself',
	'she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this',
	'that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did',
	'doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against',
	'between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under',
	'again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most',
	'other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don',
	'should','now','d','ll','m','o','re','ve','y','ain','aren','couldn','didn','doesn','hadn','hasn','haven','isn','ma','mightn',
	'mustn','needn','shan','shouldn','wasn','weren','won','wouldn','said','mr', 'obama', 'would', 'president']


def load_borowitz():
	file = open("final_borowitz.pickle",'r')
	d = pickle.load(file)
	
	titles = []
	dates = []
	urls = []
	article_text = []

	for k, v in d.items():
		titles.append(k[0])
		dates.append(k[1])
		urls.append(k[2])
		article_text.append(v)    

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Get news satire from The Borowitz Report delivered to your inbox.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Get the Borowitz Report delivered to your inbox.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Get The Borowitz Report delivered to your inbox.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("(The Borowitz Report)", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("News Satire from The Borowitz Report", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Satire from The Borowitz Report", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("This post is news satire from The Borowitz Report.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("News satire from The Borowitz Report.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Andy Borowitz will be doing a free show at Rutgers University on Monday, October 29, at 7 P.M. To register for tickets, click here.    Photograph by Lauren Lancaster.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Andy Borowitz is doing a show to benefit public radio.","")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Tickets for Andy Borowitz's next live show are now on sale.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("(Satire from The Borowitz Report)", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Illustration by Andy Borowitz.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Andy Borowitz will be doing two shows at next month's New Yorker Festival: Friday, October 5th, with the storytelling group The Moth, and Saturday, October 6th, with Sarah Silverman. Ticket information here.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("A small number of tickets have just been released for Andy Borowitz's New Yorker Festival show this Friday night in New York City. Buy tickets here.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("(Satire from The Borowitz Report)", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Tickets for Andy Borowitz's next live show are now on sale.  Photograph by Alex Wong/Getty.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Tickets for Andy Borowitz's next live show are now on sale.      Illustration by Tom Bachtell.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Andy Borowitz will be doing two shows at next month's New Yorker Festival: Friday, October 5th, with the storytelling group The Moth, and Saturday, October 6th, with Sarah Silverman. Ticket information here.    Photograph by Tony Avelar/Bloomberg/Getty Images.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("(The Borowitz Report)", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("Tickets for Andy Borowitz's next live show are now on sale.  Photograph by Chris Maddaloni/CQ Roll Call.", "")

	for i in range(len(article_text)):
		article_text[i] = article_text[i].replace("(Satire from The Borowitz Report)", "")
	return titles, dates, urls, article_text

titles, dates, urls, article_text = load_borowitz()

def get_onion_text(url):
	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page)
	#soup.prettify()
	div_x = soup.find_all("div", class_="content-text")
	return str(div_x)

def get_nytimes_text(url):
	cj = CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	p = opener.open(url)
	#print p.read()
	page = p.read()
	soup = BeautifulSoup(page)
	div_x = soup.find_all("p", class_="story-body-text story-content")
	return str(div_x)

def find_similar_borowitz(new_text):
	full_text = article_text + [new_text]
	n = len(full_text)
	tfidf_vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 4), stop_words=stop_words, min_df=1)
	tfidf_matrix = tfidf_vectorizer.fit_transform(full_text)
	M = cosine_similarity(tfidf_matrix)
	last_row = M[n-1][0:n-1]
	sorted_last_row = sorted(last_row, reverse=True)
	i = np.where(last_row==sorted_last_row[0])[0][0]
	j = np.where(last_row==sorted_last_row[1])[0][0]
	return titles[i], urls[i], titles[j], urls[j], i, j

def which_newspaper(text):
	if text.startswith('http://www.nytimes'):
		return get_nytimes_text(text)
	elif text.startswith('http://www.theonion'):
		return get_onion_text(text)
	else:
		return text

#def load_lda():
#	file = open("lda2.pickle",'r')
#	[model, corpus] = pickle.load(file)
#	topics = [sorted(model.show_topic(i, topn=10), key=lambda x: x[1], reverse=True) [:10] for i in range(100)]
#	lda_corpus = model[corpus]
#	lda_docs = [doc for doc in lda_corpus]
	#doc_topics = [[titles[i],lda_docs[i]] for i in range(len(article_text))]
#	return model, lda_docs

#model, lda_docs = load_lda()
#topics = [sorted(model.show_topic(i, topn=10), key=lambda x: x[1], reverse=True) [:10] for i in range(100)]
file = open("final_stuff.pickle",'r')
lda_docs, topics = pickle.load(file)
app = Flask(__name__)

@app.route('/')
def my_form():
	return render_template("index.html")

@app.route('/', methods=['POST'])
def my_form_post():
	text = request.form['text']
	#if text == 'stop':
	#	break
	title1, url1, title2, url2, first, second = find_similar_borowitz(which_newspaper(text))
	#model, lda_docs = load_lda()
	#topics = [sorted(model.show_topic(i, topn=10), key=lambda x: x[1], reverse=True) [:10] for i in range(100)]
	topic1 = max(lda_docs[first], key=lambda x: x[1])[0]
	topic2 = max(lda_docs[second], key=lambda x: x[1])[0]

	important = [topics[topic1][i][0] for i in range(len(topics[topic1]))]
	second_important = [topics[topic2][i][0] for i in range(len(topics[topic2]))]
	result_best1 = "Best match title: %s <br/><br/>Most important LDA topic composed of: <br/>" %title1
	result_best2 = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s <br/><br/><br/>" %tuple(important)
	result_second_best1 = "Second best match title: %s <br/><br/>Most important LDA topic composed of: <br/>" %title2
	result_second_best2 = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %tuple(second_important)
	#return '<a href="{0}">{1}</a>'.format(url1,title1), '<a href="{0}">{1}</a>'.format(url2,title2)
	#print('<a href="{0}">{1}</a>'.format(url1,title1))
	#print('<a href="{0}">{1}</a>'.format(url2,title2))
	#return '<a href="{0}">{1}</a>'.format(url,title)
	
	#<a href=url>http://stackoverflow.com</a>
	
	webbrowser.open_new_tab(url1)
	webbrowser.open_new_tab(url2)
	return result_best1 + result_best2 + result_second_best1 + result_second_best2
	#return render_template("index.html")

if __name__ == '__main__':
	app.run(debug=True)