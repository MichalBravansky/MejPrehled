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
from image_processing import *
from credentials import twitter_credentials,facebook_token

import networkx as nx

import os

threshold= 0.92
rating_threshold=10
hour_difference=24

model_path="ft_model"
morph = majka.Majka('majka.w-lt')
ft_model=FastText.load(model_path)

morph = majka.Majka('majka.w-lt')
morph.tags = False
morph.first_only = True
morph.negative = "ne"


hashtags="#czech #igerscz #czechrepublic #czech_world #dnes #zpravy #zpravodajstvi #novinky #ceskarepublika #praha #brno"

twitter_client = twitter.Api(twitter_credentials["consumer_key"],
twitter_credentials["consumer_secret"],
twitter_credentials["access_token_key"],
twitter_credentials["access_token_secret"])


with open("stopwords.txt") as f:
    stopwords = f.read().splitlines()

def preprocess_text(doc):
            
    # To lowercase
    doc = doc.lower()

    # Tokenization and lemmatization
    tokens=[[morph.find(word)[0]["lemma"] for word in nltk.word_tokenize(re.sub(r'\W', ' ', str(sentence))) if word not in stopwords and len(morph.find(word)) != 0] for sentence in nltk.sent_tokenize(doc)]

    return tokens

#selects the content of the article from the database
def get_content(article_id):
    text="select [Text] from dbo.[Paragraph] WHERE Article_ID=?"
    paragraphs=pd.read_sql_query(text, cnxn,[article_id])
    return ' '.join(paragraphs["text"].values)

now = datetime.now()
time_difference=timedelta(hours=hour_difference)

end_date=now-time_difference
command='select  Article_ID,Url, SourceType_ID,Title,ImageUrl,ReleasedDate,LastChange from dbo.[Article] WHERE Downloaded = 1 LastChange>=? ORDER BY LastChange'
articles = pd.read_sql_query(command, cnxn,[end_date])

articles["content"]=articles["article_id"].apply(lambda id: get_content(id))

articles["vector"]=articles.apply(lambda article: get_vector(preprocess_text(article)), axis=1)

end_date=articles.iloc[-1]["lastchange"]



def get_vector(doc):
    return np.mean([ft_model[token] for token in flatten(doc["title_lemmatized"]+doc["content_lemmatized"])[:50]],axis=0)

flatten = lambda l: [item for sublist in l for item in sublist]

while(True):

        while(True):
            now = datetime.now()

            #loads new or updated articles
            command='select  Article_ID,Url, NewsType_ID, SourceType_ID,Title,ImageUrl,ReleasedDate,LastChange from dbo.[Article] WHERE Downloaded = 1 AND LastChange>? ORDER BY LastChange'
            df = pd.read_sql_query(command, cnxn,[end_date])

            #if any article was added or updated
            if(len(df.index))>0:
                df["content"]=df["article_id"].apply(lambda id: get_content(id))

                df["vector"]=df.apply(lambda article: get_vector(preprocess_text(article)), axis=1)

                for index, row in df.iterrows():
                    articles = articles[articles["article_id"] !=row["article_id"]]
            
             
                articles=articles.append(df, ignore_index=True)


                articles=articles[articles["lastchange"] >now-time_difference]



                end_date=articles.iloc[-1]["lastchange"]


                #breaks the loop and tries to cluster them
                break



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

    #returns the rating of a specified cluster
    def get_rating(cluster):
            rating=0
            uniqueSources=[]
            for value in item:
                data=articles.iloc[value]["sourcetype_id"]
                if data not  in uniqueSources:
                    rating+=1
                    uniqueSources.append(data)
                rating+=1
            
            return rating

    # Creates a graph of these similarities
    for item in similarities:
        if len(item)>0:
            start=item[0]

            for i in item[1:]:
                G.add_edge(start,i)

    # Returns all cliques, a subgraph where each node is connected to every other node
    clusters=list(nx.algorithms.clique.find_cliques(G))
    clusters.sort(key=get_rating, reverse=True)

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

        
        evaluatedClusters.append({'rating':get_rating(item),'ids':item})


    evaluatedClusters.sort(key=itemgetter('rating'), reverse=True)

    for item in evaluatedClusters:
            if(item.get("rating")<=rating_threshold):
                break

            ids=item.get("ids")

            #gets the sum of all the cosine simularities
            sums=numpy.array([sum([matrix[id,other_id] for other_id in ids]) for id in ids])

            #selects the most representing article for the cluster
            row=articles.iloc[ids[sums.argmax()]]

            
            twitter_post=str(row["title"])

            #selects the article's content
            command="select [Text] from dbo.[Paragraph] WHERE Article_ID=?"
            paragraphs=pd.read_sql_query(command, cnxn,[row["article_id"]])

            imageurl=str(row["imageurl"])

            twitter_post+="\n"+row["url"]
            
            #posts to Twitter
            twitter_client.PostUpdate(twitter_post)

            image_string=get_image(imageurl,str(row["title"]),row["newstype_id"])

            #posts to Instagram
            publish_to_instagram(image_string,(textFB+"\n\n"+hashtags)) 
            
            textFB=str(paragraphs["text"][0])+"\n\nZdroj: "+row["url"]

            #posts to Facebook
            requests.post("https://graph.facebook.com/112271243613938/photos",files={'photo.png':image_string}, data={'caption':textFB, 'access_token': facebook_token})

