import re
import requests
from bs4 import BeautifulSoup


class Scraper:
    def clean_html(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        
        return cleantext

    def clean_text(self,texts):
        paragraphs=[]
        for paragraph in texts:
            paragraph_text = self.clean_html(str(paragraph)).strip()
            if not any(forbidden in paragraph_text for forbidden in ["©", "|", "a. s.", "a.s.", "s. r. o.", "s.r.o."]):
                if paragraph_text!='':
                    paragraphs.append(paragraph_text)
        return paragraphs
    
    def get_soup(self, url):
        page = requests.get(url)
        encoding = page.encoding if 'charset' in page.headers.get('content-type', '').lower() else None
        return BeautifulSoup(page.content, 'html.parser', from_encoding=encoding)

    
    def get_url_content(self, url):
        return self.clean_text(self.get_soup(url).find('article').find_all("p"))

class IDNES_Scraper(Scraper):
    def get_url_content(self, url):
        soup=super().get_soup(url)
        return super().clean_text(([soup.find("div", {"class": "opener"})]+soup.find("div", {"id": "content"}).find_all("p"))[:-14])

class Novinky_Scraper(Scraper):
    def get_url_content(self, url):
        soup=super().get_soup(url)
        return super().clean_text(soup.find('main').find_all("p")[:-10])

class Denik_Scraper(Scraper):
    def get_url_content(self, url):
        soup=super().get_soup(url)
        return super().clean_text(soup.find_all("p"))

class Aktualne_Scraper(Scraper):
    def get_url_content(self, url):
        soup=super().get_soup(url)
        return super().clean_text(([soup.find("div", {"class": "article__perex"})]+soup.find_all("p"))[:-5])

class CT24_Scraper(Scraper):
    def get_url_content(self, url):
        soup=super().get_soup(url)
        return super().clean_text(soup.find('article').find_all("p"))