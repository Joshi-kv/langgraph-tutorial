from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7)

def chat(state: MessagesState) -> MessagesState:
    return {"messages": [llm.invoke(state["messages"])]}

workflow = StateGraph(MessagesState)

workflow.add_node("chat", chat)

workflow.add_edge(START, "chat")
workflow.add_edge("chat", END)

graph = workflow.compile()

# response = graph.invoke()
