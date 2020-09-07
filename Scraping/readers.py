from scrapers import *
import pytz
import datetime
import feedparser
from dateutil import parser
utc = pytz.utc


class Feed_Reader:

    def __init__(self):
        self.last_timestamp=utc.localize(datetime.datetime.min)


    def get_article(self,entry):
        return  {'title':entry["title"],'summary':entry["summary"],'updated_date':parser.parse(entry["published"]),'url':entry["link"],'image_url':entry["media_content"][0]["url"],'channel':self.channel}

    def get_feed(self):
        articles=[]
        for entry in feedparser.parse(self.url_feed).entries:
            if parser.parse(entry["published"])<=self.last_timestamp:
                break
            try:
                article = self.get_article(entry)
            
                article["content"]=self.scraper.get_url_content(article["url"])

                articles.append(article)
            except:
                print(self.channel + " error on content downloading")

        
        if len(articles)>0:
            self.last_timestamp=articles[0]["published_date"]

        return articles

class IDNES_Reader(Feed_Reader):
    def __init__(self):
        self.channel="IDNES"
        self.url_feed="https://servis.idnes.cz/rss.aspx?c=zpravodaj"
        self.scraper=IDNES_Scraper()
        super().__init__()
    
    def get_article(self,entry):
        return  {'id':entry["id"],'title':entry["title"],'summary':entry["summary"],'updated_date':parser.parse(entry["published"]),'url':entry["link"],'image_url':entry["media_content"][0]["url"],'channel':self.channel}

    
class CT24_Reader(Feed_Reader):
    def __init__(self):
        self.channel="CT24"
        self.url_feed="https://ct24.ceskatelevize.cz/rss/hlavni-zpravy"
        self.scraper=CT24_Scraper()
        super().__init__()
    
    def get_article(self,entry):
        return  {'id':entry["id"].split('/')[-1],'title':entry["title"],'summary':entry["summary"],'updated_date':parser.parse(entry["published"]),'url':entry["link"],'image_url':entry["media_content"][0]["url"],'channel':self.channel}

class Novinky_Reader(Feed_Reader):
    def __init__(self):
        self.channel="Novinky"
        self.url_feed="https://www.novinky.cz/rss"
        self.scraper=Novinky_Scraper()
        super().__init__()
    
    def get_article(self,entry):
        return  {'id':entry["id"].split('/')[-1],'title':entry["title"],'summary':entry["summary"],'updated_date':parser.parse(entry["published"]),'url':entry["link"],'image_url':entry["szn_url"],'channel':self.channel}


class Aktualne_Reader(Feed_Reader):
    def __init__(self):
        self.channel="Aktualne"
        self.url_feed="https://www.aktualne.cz/rss/"
        self.scraper=Aktualne_Scraper()
        super().__init__()
    
    def get_article(self,entry):
        return  {'id':entry["id"],'title':entry["title"],'summary':entry["summary"],'updated_date':parser.parse(entry["published"]),'url':entry["link"],'image_url':re.search('<img src="(.*)" alt="', entry["content"][0]["value"]).group(1),'channel':self.channel}


class Denik_Reader(Feed_Reader):
    def __init__(self):
        self.channel="Denik"
        self.url_feed="https://www.denik.cz/rss/zpravy.html"
        self.scraper=Denik_Scraper()
        super().__init__()
    
    def get_article(self,entry):
        return  {'id':entry["id"].split('/')[-1],'title':entry["title"],'summary':entry["summary"],'updated_date':parser.parse(entry["published"]),'url':entry["link"],'image_url':entry["media_url"][:-7]+"630-16x9.jpg",'channel':self.channel}