from readers import *

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import sys

sys.path.insert(1, '../Clustering')

from vector_representation import *

stopwords=get_stopwords()

fasttext_model=get_fasttext_model()

majka=get_majka()

# Use a service account
cred = credentials.Certificate('mej-prehled-288419-5e22102b957f.json')

firebase_admin.initialize_app(cred)

#db = firestore.client()
#last_added_articles=db.collection(u'articles').where(u'published_date', u'>', datetime.datetime.now()-datetime.timedelta(hours=48)).order_by(u'published_date').get()[::-1]

feed_readers=[]

feed_readers.append(IDNES_Reader())
feed_readers.append(Novinky_Reader())
feed_readers.append(Aktualne_Reader())
feed_readers.append(Denik_Reader())
feed_readers.append(CT24_Reader())

while True:
    articles=[]

    for reader in feed_readers:
        articles+=reader.get_feed()

    
    for article in articles:

        db = firestore.client()
        
        doc= db.collection(u'articles').document(article["channel"]+"_"+article["id"])

        article["vector_representation"]=get_vector(article,fasttext_model,majka,stopwords)

        if doc.get().exists==True:
            doc.update(article)
        else:
            article["published_date"]=article["updated_date"]
            doc.set(article)




