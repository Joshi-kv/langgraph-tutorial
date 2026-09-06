import os

from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.messages import SystemMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama

load_dotenv(override=True)

@tool
def get_stock_price(symbol: str):
    """Return the current price of a stock given the stock symbol"""
    return({
        "MSFT": 300.00,
        "NVDA": 500.00,
        "GOOGLE": 200.00
    }).get(symbol.upper(), 0.00)
    
@tool
def purchase_stock(symbol: str, quantity: int, total_price: float):
    """Purchase a given quantity of a stock given the stock symbol and total price"""
    print(f"Attempting to purchase {quantity} shares of {symbol} for ${total_price}")
    decesion = interrupt(f"Approve buying {quantity} shares of {symbol} for ${total_price}")
    if decesion == "approve":
        return f"Successfully purchased {quantity} shares of {symbol} for ${total_price}"
    else:
        return f"Failed to purchase {quantity} shares of {symbol} for ${total_price}"
        
memory = MemorySaver()
config = {"configurable": {"thread_id": "stock_thread"}}
    
system_prompt = SystemMessage(
    content=(
        "You are a stock trading assistant. You help users check stock prices and purchase stocks.\n\n"
        "Available actions:\n"
        "- get_stock_price: look up the current price of a stock by its symbol\n"
        "- purchase_stock: buy a quantity of a stock (this requires human approval before completing)\n\n"
        "Rules:\n"
        "1. If the user wants to buy a stock but doesn't know the price, call get_stock_price first, "
        "calculate the total price (price × quantity), then call purchase_stock with that total.\n"
        "2. Call each tool only ONCE per user request. After a tool returns a result, do not call the "
        "same tool again with the same or similar arguments — use the result you already have.\n"
        "3. After receiving a tool's result, respond to the user in plain language with the outcome. "
        "Do not call any more tools once you have the information needed to answer.\n"
        "4. If a stock symbol isn't recognized (price returns $0.00), tell the user it's not available "
        "instead of proceeding with a purchase.\n"
        "5. Be concise. State the price or purchase outcome clearly, with no extra commentary."
    )
)


tools = [get_stock_price, purchase_stock]

llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    model="qwen2.5:7b",
    temperature=0
).bind_tools(tools)

def chat(state: MessagesState):
    # Convert MessagesState to a format compatible with the LLM
    # The LLM expects a list of messages, not the state object itself
    # We also need to include the system prompt in the list of messages
    messages = [system_prompt] + state["messages"]
    return {"messages": [llm.invoke(messages)]}

tool_node = ToolNode(tools)

workflow = StateGraph(MessagesState)

workflow.add_node("chat", chat)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "chat")
workflow.add_conditional_edges("chat", tools_condition)
workflow.add_edge("tools", "chat")

graph = workflow.compile()
