from typing import Literal, Optional, List
from app.models.ai import AIChange
from app.models.graph import Graph, Node, Edge
from app.utils.ids import generate_id
import json
from app.ai.ollama_client import ask_ollama, Ollama_client_error

SYSTEM_PROMPT = """
You are an AI reviewer for a graph of study notes.

You MUST return a JSON array of change objects.
Return ONLY valid JSON. No explanations. No markdown.

Each change object MUST have this structure:
{
  "type": "importance" | "rename_node",
  "node_id": "<existing node id>",
  "payload": { "to": <new value> }
}

Rules:
- You MUST return at least ONE change.
- Only suggest changes that strictly follow the structure above.
- For rename_node:
  payload MUST be exactly { "to": "<new text>" }
- For importance:
  payload MUST be exactly { "to": <integer between 1 and 10> }
- Do NOT include old values.
- Do NOT include extra keys.
- Use ONLY node IDs provided in the input.
- Do NOT invent new nodes.

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

def refine_graph(graph: Graph) -> Graph:
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

def validate_change(change: AIChange, graph: Graph) -> bool:
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
