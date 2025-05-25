import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from dotenv import load_dotenv
load_dotenv()

def message_reducer(existing_messages: list, new_message: list) -> list:
    return existing_messages + [new_message]

@tool("add_numbers")
def add_numbers(a, b) -> str:
    """Add two numbers together."""
    result = a + b
    return f"{a} + {b} = {result}"

llm = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
).bind_tools([add_numbers])

class State(TypedDict):
    """
    State of the agent.
    """
    messages: Annotated[list, message_reducer]

def chatbot(state: State):
    result = llm.invoke(state["messages"])
    return { "messages": [result] }

def tool_node(state: State):
    if state["messages"][-1][0].tool_calls:
        print(f"State: {state["messages"][-1][0].tool_calls}")
        for tool_call in state["messages"][-1][0].tool_calls:
            print(f"Tool: {tool_call["name"]}")
            if tool_call["name"] == "add_numbers":
                res = add_numbers(1,1)
                print(res)
            print(f"Tool_args: {tool_call["args"]}")
        return "tools"
    else:
        return END
    # return { "messages": [result] }

workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_node("tools", tool_node)
workflow.add_conditional_edges(
    "chatbot",
    tool_node,
    {"tools": END, END: END}
)
workflow.add_edge(START, "chatbot")
# workflow.add_edge("chatbot", END)
app = workflow.compile()

print(app.invoke({ "messages": "1 + 1は？" }))

