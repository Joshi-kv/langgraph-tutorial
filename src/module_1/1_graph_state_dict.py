from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    graph_str: str
    
def greetings(state: State) -> State:
    return {"graph_str": state["graph_str"] + "Hello World"}

builder = StateGraph(State)

builder.add_node("greetings", greetings)
builder.add_edge(START, "greetings")
builder.add_edge("greetings", END)

graph = builder.compile()

# response = graph.invoke({"graph_str": "Hi"})
# print(response)
