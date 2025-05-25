from tools_list.sqlpractice import read_summay_search
from langchain_core.tools import tool

@tool
def sql_loader(query: str):
    """
    このツールはデータベースから検索値をもとにニュース記事を出力します。
    検索値は検索しやすいよう単語で渡してください。
    """
    articles = read_summay_search(query)
    print(articles)
    return articles

# sql_loader("日産")