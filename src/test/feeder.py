import feedparser
from news_urls import urls
from sqlpractice import add_article, read_article

print(urls[0]["url"])

feed = feedparser.parse(urls[0]["url"])

for article in feed.entries:
    add_article(article.title, article.summary, article.link)

articles = read_article()

