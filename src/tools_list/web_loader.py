import bs4
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore

def web_loader(url: str):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    loader = WebBaseLoader(
        web_paths=(url,),
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                'body'
                # class_=("post-content", "post-title", "post-header")
            )
        )
    )
    docs = loader.load()

    vector_store = InMemoryVectorStore(embeddings)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    split_docs = text_splitter.split_documents(docs)

    _ = vector_store.add_documents(split_docs)
    # print(vector_store)

    return vector_store

# web_loader("https://lilianweng.github.io/posts/2023-06-23-agent/")
