from sqlalchemy import create_engine

engine = create_engine("sqlite:///src/tools_list/sqlpractice.db")

# モデル定義
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    summary = Column(String)
    url = Column(String)

Base.metadata.create_all(engine)

# データの追加
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

def add_article(title, summary, url):
    if session.query(Article).filter(Article.url == url).first():
        print("すでにデータが存在します。")
        return

    article = Article(
        title=title,
        summary=summary,
        url=url
    )
    session.add(article)
    session.commit()
    print("データが追加されました。")

def read_article():
    articles = session.query(Article).all()
    articles_obj = []
    for article in articles:
        article_obj = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "url": article.url
        }
        articles_obj.append(article_obj)
    #     print(article.title)
    #     print(article.summary)
    #     print(article.url)
    #     print("-------------------")
    return articles_obj

def read_article_by_id(id):
    article = session.query(Article).filter(Article.id == id).first()
    article_obj = {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "url": article.url
    }
    return article_obj

def read_summay_search(keyword):
    articles = session.query(Article).filter(Article.summary.like(f"%{keyword}%")).all()
    articles_obj = []
    for article in articles:
        article_obj = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "url": article.url
        }
        articles_obj.append(article_obj)
        # print(article.title)
    return articles_obj
    
def all_delete_article():
    session.query(Article).delete()
    session.commit()
    print("すべてのデータが削除されました。")

def modify_article(id, title, summary, url):
    article = session.query(Article).filter(Article.id == id).first()
    article.title = title
    article.summary = summary

