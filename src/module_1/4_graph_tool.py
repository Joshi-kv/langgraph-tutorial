from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def multiply(n1: int, n2: int) -> int:
    """Multiply two numbers"""
    return n1 * n2

@tool
def addition(n1: int, n2: int) -> int:
    """Add two numbers"""
    return n1 + n2

@tool
def subtraction(n1: int, n2: int) -> int:
    """Subtract two numbers"""
    return n1 - n2

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
).bind_tools([multiply, addition, subtraction])

def chat(state: MessagesState) -> MessagesState:
    return {"messages": [llm.invoke(state["messages"])]}

workflow = StateGraph(MessagesState)
tools_node = ToolNode([multiply, addition, subtraction])

workflow.add_node("chat", chat)
workflow.add_node("tools", tools_node)

workflow.add_edge(START, "chat")
workflow.add_conditional_edges("chat", tools_condition)
workflow.add_edge("tools", END)

graph = workflow.compile()