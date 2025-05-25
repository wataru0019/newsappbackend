import os
import bs4
from langchain_core import vectorstores
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.tools import retriever, tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from langchain_core.prompts import PromptTemplate


from dotenv import load_dotenv
load_dotenv()

from llm_list import llm_openai
from tools_list.web_loader import web_loader
from tools_list.web_search import tavily_search
from tools_list.pdf_loader import pdf_loader
from tools_list.sql_loader import sql_loader

class MasterState(TypedDict):
    """
    State of the agent.
    """
    messages: Annotated[list, add_messages]
    url: str
    context: str = ""

tools = [tavily_search, pdf_loader, sql_loader]
with_tools_llm = llm_openai.bind_tools(tools)

def chatbot(state: MasterState):
    user_input = state["messages"][-1].content
    if state["url"] == "":
        prompt = PromptTemplate.from_template("""
            ユーザーの質問に答えてください。
            なお、Toolを使うかどうか、ユーザーの質問の意図をよく考えなさい。
            あなたの知識の中から回答する方が質の良い回答ができると判断した場合は
            Toolを使う必要がありません。

            質問: {user_input}
        """)
        result = with_tools_llm.invoke([HumanMessage(content=prompt.format(user_input=user_input))])
        return { "messages": [result] }

    else :
        prompt = PromptTemplate.from_template("""
            以下のcontextを参考に、ユーザーの質問に答えてください。
            質問: {user_input}
            context: {context}
        """)
        result = with_tools_llm.invoke([HumanMessage(content=prompt.format(user_input=user_input, context=state["context"]))])
        return { "messages": [result] }

def retriever(state: MasterState):
    vectorstore = web_loader(state["url"])
    context = vectorstore.similarity_search(state["messages"][0].content)
    return { "context": context }

def review_chat(state: MasterState):
    user_input = state["messages"][0].content
    tool_input = state["messages"][-1].content
    prompt = PromptTemplate.from_template("""
        Toolの実行結果を元に、ユーザーの質問事項に沿った内容になるよう
        適切な回答を生成しなさい。
        ユーザーの質問: {user_input}
        Toolの実行結果: {tool_input}
    """)
    result = llm_openai.invoke([HumanMessage(content=prompt.format(user_input=user_input, tool_input=tool_input))])
    return { "messages": [result] }

def condition_retriever(state: MasterState):
    if state["url"] == "":
        return "chatbot"
    else:
        return "retriever"

tool_node = ToolNode(tools)

workflow = StateGraph(MasterState)
workflow.add_node("chatbot", chatbot)
workflow.add_node("retriever", retriever)
workflow.add_node("tools", tool_node) 
workflow.add_node("review_chat", review_chat)

workflow.add_conditional_edges(
    START,
    condition_retriever,
    {
        "chatbot": "chatbot",
        "retriever": "retriever"
    }
)
workflow.add_edge("retriever", "chatbot")
workflow.add_conditional_edges(
    "chatbot",
    tools_condition,
)
workflow.add_edge("tools", "review_chat")
workflow.add_edge("chatbot", END)
workflow.add_edge("review_chat", END)
app = workflow.compile()

# response = app.invoke({ "messages": [HumanMessage(content="TavilySearchResultsの使い方を教えて")], "url": "https://python.langchain.com/api_reference/community/tools/langchain_community.tools.tavily_search.tool.TavilySearchResults.html" })
response = app.invoke({ "messages": [HumanMessage(content="日産のニュースをデータベースから検索して教えて")], "url": "" })

# for tokan, matadata in app.stream(
#     { "messages": [HumanMessage(content="Expoのインストール方法を教えて")], "url": "" },
#     stream_mode="updates"
#     ):
#     print("tokan", tokan)


def agent_master(query: str):
    result = app.invoke({ "messages": [HumanMessage(content=query)], "url": "" })
    return result["messages"][-1].content

