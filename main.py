from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.pydantic_v1 import BaseModel
import uuid
from nodes import plan_node, research_plan_node, generation_node, reflection_node, research_critique_node, should_continue  

class AgentState(TypedDict):
    task: str # Essay topic
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int

class Queries(BaseModel):
    queries: List[str]


def create_graph():
    builder = StateGraph(AgentState)

    builder.add_node("planner", plan_node)
    builder.add_node("generate", generation_node)
    builder.add_node("reflect", reflection_node)
    builder.add_node("research_plan", research_plan_node)
    builder.add_node("research_critique", research_critique_node)

    builder.set_entry_point("planner")

    builder.add_conditional_edges(
        "generate", 
        should_continue, 
        {END: END, "reflect": "reflect"}
    )

    builder.add_edge("planner", "research_plan")
    builder.add_edge("research_plan", "generate")
    builder.add_edge("reflect", "research_critique")
    builder.add_edge("research_critique", "generate")

    memory = SqliteSaver.from_conn_string(":memory:")
    graph = builder.compile(checkpointer=memory)
    graph.get_graph().draw_png("graph.png")

    return graph


def run():
    graph = create_graph()
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    for s in graph.stream({
        'task': 'Cuáles son los últimos fichajes del betis',
        'max_revisions': 3,
        'revision_number': 1
    }, config):
        print(s)

if __name__ == "__main__":
    run()
