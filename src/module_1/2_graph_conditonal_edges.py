from langgraph.graph import StateGraph, START, END
from typing import Literal
from typing_extensions import TypedDict

class State(TypedDict):
    graph_str: str
    
def node1(state:State) -> State:
    return {"graph_str": state["graph_str"]}

def node2(state: State) -> State:
    return {"graph_str": state["graph_str"] + "Node 2"}

def node3(state: State) -> State:
    return {"graph_str": state["graph_str"] + "Node 3"}

def next_step(state: State) -> Literal["node2", "node3"]:
    word = state['graph_str'].lower()
    if word.startswith("hi"):
        return "node2"
    
    return "node3"

workflow = StateGraph(State)

workflow.add_node("node1", node1)
workflow.add_node("node2", node2)
workflow.add_node("node3", node3)

workflow.add_edge(START, "node1")
workflow.add_conditional_edges(
    "node1",
    next_step,
)
workflow.add_edge("node2", END)
workflow.add_edge("node3", END)

graph = workflow.compile()

# response = graph.invoke({"graph_str": "Hi"})
# print(response )