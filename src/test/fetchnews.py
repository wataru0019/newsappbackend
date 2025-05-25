import requests
from src.test.sqlpractice import read_article_by_id
from bs4 import BeautifulSoup

def get_article_description(id):
    article = read_article_by_id(id)
    url = article["url"]
    res = requests.get(url)
    decode_content = res.content.decode("utf-8")
    soup = BeautifulSoup(decode_content, "html.parser")
    content = soup.find("div", class_="content--detail-body")
    if content:
        raw_text = content.get_text()
        trimmed_text = raw_text.strip()
        print(trimmed_text)
        return trimmed_text
    else:
        print("content not found")
        return None
