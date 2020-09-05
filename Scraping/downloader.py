from readers import *

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('mej-prehled-288419-5e22102b957f.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

feed_readers=[]

feed_readers.append(IDNES_Reader())
feed_readers.append(Novinky_Reader())
feed_readers.append(Aktualne_Reader())
feed_readers.append(Denik_Reader())
feed_readers.append(CT24_Reader())

collection_ref=db.collection(u'articles')

while True:
    articles=[]

    for reader in feed_readers:
        articles+=reader.get_feed()

    for article in articles:

        doc= db.collection(u'articles').document(article["channel"]+"_"+article["id"])

        if doc.get().exists==True:
            doc.update(article)
        else:
            doc.set(article)




