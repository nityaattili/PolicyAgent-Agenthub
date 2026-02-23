from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from app.agent.nodes import validate_input, retrieve_docs, draft_answer, post_check


class AgentState(TypedDict):
    user_role: str
    question: str
    retrieved_chunks: List[Dict[str, Any]]
    answer: str
    citations: List[Dict[str, Any]]
    guardrail_flags: List[str]
    status: str


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("validate", validate_input)
    g.add_node("retrieve", retrieve_docs)
    g.add_node("draft", draft_answer)
    g.add_node("post_check", post_check)

    g.set_entry_point("validate")
    g.add_edge("validate", "retrieve")
    g.add_edge("retrieve", "draft")
    g.add_edge("draft", "post_check")
    g.add_edge("post_check", END)

    return g.compile()


GRAPH = build_graph()
