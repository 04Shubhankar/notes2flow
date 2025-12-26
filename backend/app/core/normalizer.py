from typing import List, Tuple, Any, Dict
from app.models.input import InputNode

def normalize_input(nodes: List[Dict[str, Any]]) -> Tuple[List[InputNode], List[Dict[str, Any]]]:
    normalized = []
    corrections = []

    for idx, raw in enumerate(nodes):
        original = raw.get("importance")

        try:
            importance = int(original)
        except (TypeError, ValueError):
            importance = 1
            corrections.append({
                "index": idx,
                "field": "importance",
                "from": original,
                "to": importance,
                "reason": "invalid or missing importance"
            })

        if importance <= 0:
            corrections.append({
                "index": idx,
                "field": "importance",
                "from": original,
                "to": 1,
                "reason": "importance must be >= 1"
            })
            importance = 1

        normalized.append(
            InputNode(
                text=raw.get("text", "").strip(),
                importance=importance
            )
        )

    return normalized, corrections
