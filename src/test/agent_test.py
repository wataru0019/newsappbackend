import os
import bs4
from langchain_core import vectorstores
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.tools import retriever, tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from langchain_tavily import TavilySearch
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
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

def test_reducer(current_value: any, new_value: any):
    """
    このテストは、langgraphのReducerの機能をテストするためのものです。
    Reducerは、グラフの状態を変更する関数です。
    """
    return { "num": new_value }

@tool
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    result = a + b
    return str(result)

# @tool
# def human_assistance(query: str) -> str:
#     """Request assistance from a human."""
#     print(f"Human assistance requested: {query}")
#     human_response = interrupt({"query": query})
#     print(f"Human response: {human_response}")
#     return human_response["data"]

tavily_search = TavilySearch(max_results=2)

tools = [add_numbers, tavily_search]
tool_node = ToolNode(tools)

class State(TypedDict):
    """
    State of the agent.
    """
    messages: Annotated[list, add_messages]
    test_num: Annotated[str, test_reducer]
    context: str = ""

def retriever(state: State):
    context = vector_store.similarity_search(state["messages"][0].content)
    return { "context": context }

def chatbot(state: State):
    llm_bind_tools = llm.bind_tools(tools)
    prompt = HumanMessage(
        content=f"以下のコンテキストを参考に、'{state['messages'][0].content}'に回答してください。\nコンテキスト: {state['context']}"
    )
    result = llm_bind_tools.invoke([prompt])
    new_num = state["test_num"]["num"] + state["test_num"]["num"]
    return { "messages": [result], "test_num": new_num }

def re_chatbot(state: State):
    result = llm.invoke([HumanMessage(f"'{state['messages'][0].content}'の問いに対し'{state['messages'][-1].content}'が正しい答えになっているかを判断せよ")])
    return { "messages": [result], "test_num": state["test_num"]["num"] + state["test_num"]["num"] }

def judge_node(state: State):
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_node("retriever", retriever)
workflow.add_node("re_chatbot", re_chatbot)
workflow.add_node("tools", tool_node)
workflow.add_conditional_edges(
    "chatbot",
    judge_node,
    { "tools": "tools", END: "re_chatbot" }
)
workflow.add_edge(START, "retriever")
workflow.add_edge("retriever", "chatbot")
workflow.add_edge("tools", "chatbot")
workflow.add_edge("re_chatbot", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

user_input: str = input("ユーザーの入力: ")
res = app.invoke(
    { "messages": [user_input], "test_num": "0" },
    # { "messages": human_command },
    config,
    # interrupt_after="chatbot"
    )
print(f"AIレスポンス: {res["messages"][-1].content}")

# user_input = input("ユーザーの入力: ")

# res2 = app.invoke(
#     { "messages": [HumanMessage(user_input)], "test_num": "1" },
#     # { "messages": human_command },
#     config,
#     # interrupt_before="re_chatbot"
#     )

# print(f"AIレスポンス: {res2["messages"][-1].content}")

# for status in app.get_state_history(config):
#     print("Num Messages: ", len(status.values["messages"]), "Next: ", status.next)
#     print(status.values)
#     print("-" * 80)
