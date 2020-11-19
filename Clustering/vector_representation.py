from gensim.models.fasttext import FastText
import nltk
import majka
import re
import numpy as np
import math

def get_vector(article,ft_model,morph,stopwords):
    
    doc = article["title"]+" ".join(article["content"])
    # To lowercase
    doc = doc.lower()

    # Tokenization and lemmatization
    tokens=[[morph.find(word)[0]["lemma"] for word in nltk.word_tokenize(re.sub(r'\W', ' ', str(sentence))) if word not in stopwords and len(morph.find(word)) != 0] for sentence in nltk.sent_tokenize(doc)]

    flatten = lambda l: [item for sublist in l for item in sublist]

    if len(flatten(tokens))==0:
        return None

    vector= np.mean([ft_model[token] for token in flatten(tokens)[:50]],axis=0)

    
    return [float(data) for data in vector]


def get_fasttext_model():

    return FastText.load("../Clustering/model_best")

def get_majka():
    morph = majka.Majka('../Clustering/majka.w-lt')
    morph.tags = False
    morph.first_only = True
    morph.negative = "ne"

    return morph

def get_stopwords():
    with open("../Clustering/stopwords.txt",encoding="utf-8") as f:
        stopwords = f.read().splitlines()
    return stopwords