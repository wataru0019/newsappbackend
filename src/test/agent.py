import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.tools import Tool

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    result = a + b
    return f"{a} + {b} = {result}"

add_tool = Tool(
    func=add_numbers,
    name="add_numbers",
    description="2つの数値を足し算します。ユーザーは「aに[数値]、bに[数値]を足して」のように指示してください。"
)

tool_node = ToolNode([add_tool])

class State(TypedDict):
    """
    State of the agent.
    """
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    llm = ChatOpenAI(
        model="gpt-4o-mini-2024-07-18",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
    ).bind_tools([add_tool])
    return { "messages": [llm.invoke(state["messages"])] }

def route_node(state: State):
    """tool_nodeの呼び出し要否を判定する"""
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    route_node,
    {"tools": "tools", END: END}
)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("tools", "chatbot")
graph = graph_builder.compile()

def get_env(str):
    # prompt = PromptTemplate.from_template("{str}")
    # llm = ChatOpenAI(
    #     model="gpt-4o-mini-2024-07-18",
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     temperature=0,
    # )
    # parser = StrOutputParser()
    # chain = prompt | llm | parser
    # result = chain.invoke({"str": str})
    result = graph.invoke({"messages": [{"role": "user", "content": str}]})
    return result