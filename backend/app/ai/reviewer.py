from typing import Literal, Optional, List
from pydantic import BaseModel
from app.core.builder import BuiltGraph

AI_ALLOWED_CHANGES = {
    "importance": "auto",
    "add_node": "review",
    "remove_node": "review",
    "rename_node": "review",
}

class AIChange(BaseModel):
    type: Literal["importance", "add_node", "remove_node", "rename_node"]
    node_id: Optional[str]
    payload: dict
    
def serialize_graph(graph: BuiltGraph) -> dict:
    return{
        "nodes":[
            {
                "id": node.id,
                "label": node.label,
                "importance": node.importance,
                "parent_id": getattr(node, "parent_id", None),
            }
            for node in graph.nodes.values()
        ]
    }

def ai_review(graph: BuiltGraph) -> List[AIChange]:
    """
    AI reviewer stub.
    Must return structured AIChange objects only.
    """
    # later: serialize graph + send to Ollama
    return []

def refine_graph(graph: BuiltGraph) -> BuiltGraph:
    changes = ai_review(graph)

    for change in changes:
        rule = AI_ALLOWED_CHANGES.get(change.type)
        if not rule:
            continue

        if rule == "auto":
            graph.apply_change(change)

        elif rule == "review":
            if validate_change(change, graph):
                graph.apply_change(change)

    return graph

def validate_change(change: AIChange, graph: BuiltGraph) -> bool:
    if change.type == "rename_node":
        to = change.payload.get("to")
        return isinstance(to, str) and len(to) <= 50

    if change.type == "add_node":
        return graph.node_count < 500

    if change.type == "remove_node":
        return change.node_id is not None and not graph.is_root(change.node_id)

    if change.type == "importance":
        val = change.payload.get("to")
        return isinstance(val, int) and 1 <= val <= 10

    return False
