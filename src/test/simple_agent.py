import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

llm = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,   
)

def add_messages(existing_messages: list, new_messages: list) -> list:
    """Add two lists together."""
    result = existing_messages + new_messages
    return result

@tool("wataru_kashihara")
def wataru_kashihara():
    """
    このtoolは柏原亘（カシハラワタル）の情報を返す関数です。
    返すことのできる情報は以下のとおりです。
    1. 柏原亘（カシハラワタル）の名前
    2. 柏原亘（カシハラワタル）の誕生日
    3. 柏原亘（カシハラワタル）の血液型
    """
    name = "柏原亘（カシハラワタル）"
    birthday = "1996年1月21日"
    blood_type = "A型"
    return f"{name}の誕生日は{birthday}です。血液型は{blood_type}です。"

llm_bind_tools = llm.bind_tools([wataru_kashihara])

class State(TypedDict):
    """
    State of the agent.
    """
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    prompt = PromptTemplate.from_template("{messages}")
    parser = StrOutputParser()
    chain = prompt | llm_bind_tools | parser
    result = chain.invoke({ "messages": state["messages"] })
    return { "messages": [result] }

# def deep_inspect(state: State):
#     prompt = PromptTemplate.from_template(
#         """
#         以下のメッセージを詳しく調べて本当に正しい答えかどうかを検証してください。
#         本当に正しい答えと思われるなら、その理由を示してください。
#         本当に正しい答えでないなら、その理由を示してください。
#         答えは必ずしも正しい答えである必要はありません。
        
#         {messages}
#         """
#     )
#     parser = StrOutputParser()
#     chain = prompt | llm_bind_tools | parser
#     result = chain.invoke({ "messages": state["messages"][-1] })
#     return { "messages": [result] }

workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
# workflow.add_node("deep_inspect", deep_inspect)
workflow.add_edge(START, "chatbot")
# workflow.add_edge("chatbot", "deep_inspect")
workflow.add_edge("chatbot", END)
app = workflow.compile()

chat = app.invoke({ "messages": [{"role": "user", "content": "柏原亘の誕生日は?"}] })

print(chat)

