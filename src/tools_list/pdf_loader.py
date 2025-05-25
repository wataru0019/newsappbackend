import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool

@tool
def pdf_loader(query: str):
    """
    このツールはExpoを使ったWeb開発の方法が記載されたPDFを読み込んで
    ユーザーからのインプットに応じてPDFの内容を適切に回答します。
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path を os.path.abspath() で正規化する
    file_path = os.path.abspath(os.path.join(current_dir, "..", "static", "ExpoWeb_0918.pdf"))

    # デバッグ用に実際のパスを表示してみるのも良いでしょう
    # print(f"Attempting to load PDF from: {file_path}")

    loader = PyPDFLoader(file_path)
    pages = []
    pages = loader.load()
    for page in loader.load():
        # print(page.page_content)
        pages.append(page)

    vector_store = InMemoryVectorStore.from_documents(pages, OpenAIEmbeddings(model="text-embedding-3-small"))
    docs = vector_store.similarity_search(query, k=2)
    docs_text = ""
    for doc in docs:
        docs_text += doc.page_content + "\n"
        # print(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')

    return docs_text