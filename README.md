# Borowitz App
### You can input any New York Times article URL, a URL of an article from The Onion, or any text you want and the app will find a Borowitz Report most similar to your article/text.  Articles are converted to numerical vectors using a TF-IDF Vectorizer.  Similarity is measured using cosine similarity.
### Try it for yourself [here](http://velocci.pythonanywhere.com/ "My PythonAnywhere Site").
### Or try it on your machine by downloading this repository and running the borowitz_app.py file.
### (I recently updated the code for Python 3.)

### Updated August 14, 2018: Added another version of the app (borowitz_app_glove.py) that does the same thing but uses the GloVe word embedding instead of a TF-IDF Vectorizer. It seems to work better! For example, try the New York Times article URL: https://www.nytimes.com/2018/08/12/technology/google-facebook-dominance-hurts-ad-tech-firms-speeding-consolidation.html
Note: You'll have to run various cells from borowitz_glove.ipynb to download, unzip, process, and pickle the glove.6B word embeddings.

### Updated August 15, 2018: Added another version of the app (borowitz_app_word2vec.py) that does the same thing but uses Google's pre-trained Word2Vec model.
Note: You'll have to run various cells from borowitz_word2vec.ipynb to download the model.
