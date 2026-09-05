from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage

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

tools = [multiply, addition, subtraction]

system_message = SystemMessage(
    content=(
        "You are a helpful math teacher.\n"
        "If the user asks a math related question, use the available tools to answer the question.\n"
        "Otherwise, just answer no tools available.\n"
        "Always give a short summary after the answer."
    )
)

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
).bind_tools(tools)

def chat(state: MessagesState) -> MessagesState:
    # Prepend the system prompt so the LLM sees the instructions every turn
    messages = [system_message] + state["messages"]
    return {"messages": [llm.invoke(messages)]}

workflow = StateGraph(MessagesState)
tools_node = ToolNode(tools)

workflow.add_node("chat", chat)
workflow.add_node("tools", tools_node)

workflow.add_edge(START, "chat")
workflow.add_conditional_edges("chat", tools_condition)
workflow.add_edge("tools", "chat")

graph = workflow.compile()
