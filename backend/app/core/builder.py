from typing import List, Dict
from app.models.input import InputNode
from app.ai.reviewer import AIChange

class BuiltGraph:
    def __init__(self, nodes: List[InputNode]):
        self.nodes: Dict[str, InputNode] = {
            node.id: node for node in nodes
        }
        self.node_count = len(self.nodes)

    def apply_change(self, change: AIChange) -> None:
        if change.type == "importance":
            self._apply_importance(change)

        elif change.type == "rename_node":
            self._apply_rename_node(change)

        elif change.type == "add_node":
            self._apply_add_node(change)

        elif change.type == "remove_node":
            self._apply_remove_node(change)

    def is_root(self, node_id: str) -> bool:
        node = self.nodes.get(node_id)
        return node and node.parent_id is None
