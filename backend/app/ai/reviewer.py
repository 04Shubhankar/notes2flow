from typing import Literal, Optional, List
from app.models.ai import AIChange
from app.models.graph import Graph, Node, Edge
from app.utils.ids import generate_id
import json
from app.ai.ollama_client import ask_ollama, Ollama_client_error

SYSTEM_PROMPT = """
You are an AI reviewer for a graph of study notes.

You MUST return a JSON array of change objects.
Return ONLY valid JSON. No explanations. No markdown. No code fences.

Each change object MUST have this structure:
{
  "type": "importance" | "rename_node",
  "node_id": "<existing node id>",
  "payload": { "to": <new value> }
}

Your two jobs:
1. SIMPLIFY JARGON: If a node label uses technical jargon or complex language,
   rename it to plain simple language that a student can understand.
   Keep labels short (max 6 words). Use rename_node for this.

2. FIX LOGICAL RELATIONS: Review the graph structure. If a node's label does
   not logically belong under its parent, rename it to make the relationship
   clear and meaningful. Use rename_node for this.

Rules:
- Return an empty array [] if no changes are needed. Do NOT force changes.
- Only use node IDs provided in the input. Do NOT invent new node IDs.
- For rename_node: payload MUST be exactly { "to": "<new text>" }
- For importance: payload MUST be exactly { "to": <integer between 1 and 10> }
- Do NOT include old values or extra keys.
- Do NOT wrap response in markdown or code fences.
"""

AI_ALLOWED_CHANGES = {
    "importance": "auto",
    "add_node": "review",
    "remove_node": "review",
    "rename_node": "review",
}

    
def serialize_graph(graph: Graph) -> dict:
    return {
        "nodes": [
            {
                "id": node.id,
                "text": node.label,
                "importance": node.importance,
            }
            for node in graph.nodes
        ]
    }

def ai_review(graph: Graph) -> List[AIChange]:
    graph_data = serialize_graph(graph)

    try:
        raw = ask_ollama(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=json.dumps(graph_data),
        )
        print("\n[AI RAW OUTPUT]")
        print(raw)

        parsed = json.loads(raw)
    except (Ollama_client_error,json.JSONDecodeError):
        return[]
    
    if not isinstance(parsed,list):
        return[]
    
    changes: List[AIChange] = []

    for item in parsed:
        try:
            changes.append(AIChange.model_validate(item))
        except Exception:
            continue
            
    return changes

def apply_change(graph: Graph, change: AIChange) -> Graph:
    nodes = list(graph.nodes)
    edges = list(graph.edges)

    if change.type == "importance":
        new_importance = change.payload.get("to")
        if isinstance(new_importance, int):
            nodes = [
                Node(
                    id=n.id,
                    label=n.label,
                    importance=new_importance if n.id == change.node_id else n.importance,
                    type=n.type
                )
                for n in nodes
            ]

    elif change.type == "rename_node":
        new_label = change.payload.get("to")
        if isinstance(new_label, str):
            nodes = [
                Node(
                    id=n.id,
                    label=new_label if n.id == change.node_id else n.label,
                    importance=n.importance,
                    type=n.type
                )
                for n in nodes
            ]

    elif change.type == "remove_node":
        nodes = [n for n in nodes if n.id != change.node_id]
        edges = [e for e in edges if e.from_node != change.node_id and e.to_node != change.node_id]

    return Graph(
        graph_id=graph.graph_id,
        nodes=nodes,
        edges=edges,
        version=graph.version + 1
    )

def refine_graph(graph: Graph) -> Graph:
    changes = ai_review(graph)

    for change in changes:
        rule = AI_ALLOWED_CHANGES.get(change.type)
        if not rule:
            continue

        if rule == "auto":
            graph = apply_change(graph, change)

        elif rule == "review":
            if validate_change(change, graph):
                graph = apply_change(graph, change)

    return graph

def validate_change(change: AIChange, graph: Graph) -> bool:
    if change.type == "rename_node":
        to = change.payload.get("to")
        return isinstance(to, str) and len(to) <= 50

    if change.type == "add_node":
        return len(graph.nodes) < 500

    if change.type == "remove_node":
        if change.node_id is None:
            return False
        target_nodes_with_parents = {e.to_node for e in graph.edges}
        return change.node_id in target_nodes_with_parents

    if change.type == "importance":
        val = change.payload.get("to")
        return isinstance(val, int) and 1 <= val <= 10

    return False
