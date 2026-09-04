from langgraph.graph import StateGraph, START, END


def node_func(state: str) -> str:
    return state + "!"

builder = StateGraph(str)

builder.add_node("nodefunc", node_func)

builder.add_edge(START, "nodefunc")
builder.add_edge("nodefunc", END)

graph = builder.compile()

response = graph.invoke("Hello World")
print(response)