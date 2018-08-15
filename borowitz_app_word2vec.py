import numpy as np
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.request import urlopen
import string
import json
import webbrowser
import gensim
import pickle
from flask import Flask
from flask import request
from flask import render_template

stop_words = stopwords.words('english')
stop_words.extend(['would','said'])

model_word2vec = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)  

word_vectors = model_word2vec.wv

def load_borowitz_word2vec():
    with open('final_borowitz_glove.json', 'r') as fp:
        borowitz = json.load(fp)
        fp.close()
        borowitz_articles = []
        for article in borowitz:
            article[3] = [word for word in article[3] if word in word_vectors.vocab]
            borowitz_articles.append(article[3])
    return borowitz, borowitz_articles

borowitz, borowitz_articles = load_borowitz_word2vec()

def get_onion_text_word2vec(page_url):
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
    article_text = [word for word in article_text if word in word_vectors.vocab]
    return article_text

def get_nytimes_text_word2vec(page_url):
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
    article_text = [word for word in article_text if word in word_vectors.vocab]
    return article_text

def find_similar_borowitz_word2vec(new_text):
    if not new_text:
    	return "You only entered a combination of stop words and words not in the Word2Vec vocabulary!  Please try again."
    scores = []
    for borowitz_article in borowitz_articles:
        score = model_word2vec.n_similarity(borowitz_article, new_text)
        scores.append(score)
    indices = [b[0] for b in sorted(enumerate(scores),key=lambda i:i[1], reverse=True)]
    i = indices[0]
    j = indices[1]
    return borowitz[i][0], borowitz[i][2], borowitz[j][0], borowitz[j][2], i, j

def which_newspaper_word2vec(text):
    start_nyt = ['https://www.nytimes.com', 'http://www.nytimes.com', 'www.nytimes.com', 'https://mobile.nytimes.com', 'http://mobile.nytimes.com']
    http = ['http://', 'https://']
    if any(text.startswith(beginning) for beginning in start_nyt):
        return get_nytimes_text_word2vec(text)
    elif any(text.startswith(beginning) for beginning in http) and 'theonion.com' in text:
        return get_onion_text_word2vec(text)
    else:
        text = "".join((char.lower() for char in text if char not in string.punctuation))
        text = text.replace('"', " ").replace("'",'').replace('“',' ').replace('”',' ').replace("’",'').replace('-',' ').replace('--',' ').replace('—',' ').replace('…',' ')
        text = [word for word in text.split() if word not in stop_words]
        text = [word for word in text if word in word_vectors.vocab]
    return text

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
	#if [x.lower() for x in text.split() if x.lower() in stop_words or x.lower() not in word_vectors.vocab]:
	#	return "You only entered a combination of stop words and words not in the Word2Vec vocabulary!  Please try again."
	#if text == 'stop':
	#	break
	try:
		title1, url1, title2, url2, first, second = find_similar_borowitz_word2vec(which_newspaper_word2vec(text))
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
	except:
		error_statement = find_similar_borowitz_word2vec(which_newspaper_word2vec(text))
		return error_statement
	#return render_template("index.html")

if __name__ == '__main__':
	app.run(debug=True)