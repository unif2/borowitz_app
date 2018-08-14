from flask import Flask
from flask import request
from flask import render_template
from urllib.request import urlopen
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import string
import json
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import webbrowser
#import os

stop_words = stopwords.words('english')

with open('glove_dictionaries.pickle', 'rb') as f:
    glove_dict = pickle.load(f)
    f.close()
    
class WordVectorizer50DMean(object):
    def __init__(self, worddict):
        self.worddict = worddict
        self.dim = len(worddict['hello']) # length of the word vectors

    def transform(self, X):
        return np.mean([self.worddict[word] if word in self.worddict else np.zeros(self.dim) for word in X], axis=0)
    
words = glove_dict['50d']
model = WordVectorizer50DMean(words)

def load_borowitz():
    with open('final_borowitz_glove.json', 'r') as fp:
        borowitz = json.load(fp)
        fp.close()
    borowitz_articles = []
    for article in borowitz:
        borowitz_articles.append(list(model.transform(article[3])))
    return borowitz, borowitz_articles

borowitz, borowitz_articles = load_borowitz()

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
    article_text = [word for word in article_text.split() if word not in stop_words]
    article_text = [list(model.transform(article_text))]
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
    article_text = [word for word in article_text.split() if word not in stop_words]
    article_text = [list(model.transform(article_text))]
    return article_text

def find_similar_borowitz(new_text):
    borowitz_articles.extend(new_text)
    M = np.matrix(borowitz_articles)
    similarity_scores = cosine_similarity(M)
    n = similarity_scores.shape[0]
    last_row = similarity_scores[n-1][0:n-1]
    sorted_last_row = sorted(last_row, reverse=True)
    i = np.where(last_row==sorted_last_row[0])[0][0]
    j = np.where(last_row==sorted_last_row[1])[0][0]
    return borowitz[i][0], borowitz[i][2], borowitz[j][0], borowitz[j][2], i, j

def which_newspaper(text):
    start_nyt = ['https://www.nytimes.com', 'http://www.nytimes.com', 'www.nytimes.com', 'https://mobile.nytimes.com', 'http://mobile.nytimes.com']
    http = ['http://', 'https://']
    if any(text.startswith(beginning) for beginning in start_nyt):
        return get_nytimes_text(text)
    elif any(text.startswith(beginning) for beginning in http) and 'theonion.com' in text:
        return get_onion_text(text)
    else:
        text = "".join((char.lower() for char in text if char not in string.punctuation))
        text = text.replace('"', " ").replace("'",'').replace('“',' ').replace('”',' ').replace("’",'').replace('-',' ').replace('--',' ').replace('—',' ').replace('…',' ')
        text = [word for word in text.split() if word not in stop_words]
        text = [list(model.transform(text))]
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