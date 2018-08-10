from flask import Flask
from flask import request
from flask import render_template
from urllib.request import urlopen
from bs4 import BeautifulSoup
import string
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import webbrowser
#import os

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
    with open('final_borowitz.json', 'r') as fp:
        d = json.load(fp)
    titles = []
    dates = []
    urls = []
    article_text = []

    for article in d:
        titles.append(article[0])
        dates.append(article[1])
        urls.append(article[2])
        article_text.append(article[3])
    fp.close()
    return titles, dates, urls, article_text

titles, dates, urls, article_text = load_borowitz()

def get_onion_text(page_url):
    page = urlopen(page_url)
    soup = BeautifulSoup(page, "html.parser")
    stuff = soup.find_all("p", attrs={"class":None})
    article_text = ""
    for things in stuff:
        blah = things.text.strip()
        article_text += blah + ' '
    article_text = "".join((char.lower() for char in article_text if char not in string.punctuation))
    article_text = article_text.replace('"', " ").replace("'",'').replace('“',' ').replace('”',' ').replace("’",'').replace('-',' ').replace('--',' ').replace('—',' ').replace('…',' ')
    return article_text

def get_nytimes_text(page_url):
    page = urlopen(page_url)
    soup = BeautifulSoup(page, "html.parser")
    stuff = soup.find_all("div", attrs={"class":"css-18sbwfn StoryBodyCompanionColumn"}) # Updated August 9, 2018
    article_text = ""
    for things in stuff:
        blah = things.text.strip()
        article_text += blah + ' '
    article_text = "".join((char.lower() for char in article_text if char not in string.punctuation))
    article_text = article_text.replace('"', " ").replace("'",'').replace('“',' ').replace('”',' ').replace("’",'').replace('-',' ').replace('--',' ').replace('—',' ').replace('…',' ')
    return article_text

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
    start_nyt = ['https://www.nytimes.com', 'http://www.nytimes.com', 'www.nytimes.com', 'https://mobile.nytimes.com', 'http://mobile.nytimes.com']
    http = ['http://', 'https://']
    if any(text.startswith(beginning) for beginning in start_nyt):
        return get_nytimes_text(text)
    elif any(text.startswith(beginning) for beginning in http) and 'theonion.com' in text:
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
file = open("final_stuff.pickle",'rb')
lda_docs, topics = pickle.load(file)
file.close()
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