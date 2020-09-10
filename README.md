# Mej Prehled

A winning project of the czech Students` Professional Activities (https://www.soc.cz/english/)

Video in czech: https://www.youtube.com/watch?v=_6Ak-QOZKQo&t=3s&ab_channel=MichalBravansk%C3%BD

# Description

The goal of this project is to create an automated news reporter on social media. Project consists of two parts, scrapers and clustering algorithm. The idea of this project
is that we can evaluate the importance of a event by essensially looking how many articles were written about him.


The scrapers download news articles from multiple sources which are then saved to a database. Firstly, they open RSSFeed and then retrive other missing information from HTML.

The articles are vectorize by custom FastText model. A similarity matrix is made which is then ran through a custom clustering algorithm based on DBSCAN. We then get a list
of clusters, which essensially describes each event.

We then evalute these clusters. If program deems cluster important enough, it publishes a new post on social media.

# Results

The results can be seen on numerous social media accounts (in czech):

Facebook: https://www.facebook.com/mejprehled
Twitter: https://twitter.com/MPrehled
Instagram: https://www.instagram.com/mej_prehled/?hl=cs
