import spacy
import pandas as pd
from datetime import datetime,timedelta
import numpy as np
from io import BytesIO
import time
from stop_words import get_stop_words
import json
import majka
from gensim.models.fasttext import FastText
import gensim
import re
from operator import itemgetter
import sys
import nltk
from multiprocessing import Pool

import networkx as nx

import os
DIR_PATH = os.getcwd()
 
path= sys.argv[1] if len(sys.argv) > 1 else r"newscrawl.csv"
threshold= float(sys.argv[2]) if len(sys.argv) > 2 else 0.88
save= int(sys.argv[3]) if len(sys.argv) > 3 else 1

morph = majka.Majka('majka.w-lt')
ft_model=FastText.load(str(DIR_PATH)+"\\model_best")

morph = majka.Majka('majka.w-lt')
morph.tags = False
morph.first_only = True
morph.negative = "ne"


with open(str(DIR_PATH)+"\\stopwords.txt") as f:
    stopwords = f.read().splitlines()

def preprocess_text(doc):
            
    # To lowercase
    doc = doc.lower()

    # Tokenization and lemmatization
    tokens=[[morph.find(word)[0]["lemma"] for word in nltk.word_tokenize(re.sub(r'\W', ' ', str(sentence))) if word not in stopwords and len(morph.find(word)) != 0] for sentence in nltk.sent_tokenize(doc)]

    return tokens

# Loads articles
articles = pd.read_csv(path,encoding ='utf8', sep=';', header=None,names=["title", "content","source", "url", "published_time"]) 

# Lemmatizes them
articles["title_lemmatized"]=articles["title"].apply(lambda title: preprocess_text(title))

articles["content_lemmatized"]=articles["content"].apply(lambda content: preprocess_text(content))


def get_vector(doc):
    return np.mean([ft_model[token] for token in flatten(doc["title_lemmatized"]+doc["content_lemmatized"])[:50]],axis=0)

flatten = lambda l: [item for sublist in l for item in sublist]

# Vectorization
articles["vector_representation"]=articles.apply(lambda article: get_vector(article), axis=1)

# Creates 1 dimensional matrix
V = np.ndarray(shape=(len(articles),200))
for id in range(0,len(articles)):
    V[id]=np.array(articles.iloc[id]["vector_representation"])

# Normalizes vectors
Vnorm = V / np.linalg.norm(V, axis=1, keepdims=True)

# Dots the matrix with itself and creates similarity matrix
matrix = Vnorm.dot(Vnorm.T)

def get_similar(id):
    similarity=[]
    for i in range(id,len(articles)):
        if matrix[id, i]>threshold:
            similarity.append(i)
    return similarity


# Returns all the articles where cosine distance is smaller than the threshold
similarities=[get_similar(i) for i in range(0,len(articles))]

G=nx.Graph()

# Creates a graph of these similarities
for item in similarities:
    if len(item)>0:
        start=item[0]

        for i in item[1:]:
            G.add_edge(start,i)

# Returns all cliques, a subgraph where each node is connected to every other node
clusters=list(nx.algorithms.clique.find_cliques(G))
clusters.sort(key=len, reverse=True)

# Creates a subset of these cliques, so each document is dedicated to only one subset
best=[]
used=[False]*len(articles)
for i in range(0,len(clusters)):
    finished=True
    for r in clusters[i]:
        if used[r]:
            finished=False
            break
            
    if finished:
        for r in clusters[i]:
            used[r]=True
        best.append(clusters[i])


evaluatedClusters=[]

# Evaluates each cluster based on their size and number of unique sources
for item in best:
    if(len(item)<=1):
        break

    rating=0
    uniqueSources=[]
    for value in item:
        data=articles.iloc[value]["source"]
        if data not  in uniqueSources:
            rating+=1
            uniqueSources.append(data)
        rating+=1
    
    evaluatedClusters.append({'rating':rating,'ids':item})

file=None

# if saving is enabled, opens file
if save==1:
    file = open('results/data'+str(int(round(time.time() * 1000)))+".txt", 'w+',encoding="utf8")

evaluatedClusters.sort(key=itemgetter('rating'), reverse=True)

for item in evaluatedClusters:
    ids=item.get("ids")

    # selects the doc which represents the cluster the most
    sums=np.array([sum([matrix[id,other_id] for other_id in ids]) for id in ids])
    row=articles.iloc[ids[sums.argmax()]]
    
    print(str(item.get("rating"))+" "+row["url"])

    # writes content to file
    if save==1:
        for id in item.get("ids"):
            file.write(str(articles.iloc[id]["content"]))
            file.write("\r\n")

        file.write("\r\n \r\n \r\n")

if save==1:
    file.close()
