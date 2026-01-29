from typing import List, Dict
from app.models.input import InputNode
from app.models.ai import AIChange
from app.utils.ids import generate_id


class BuiltGraph:
    def __init__(self, nodes):
        self.nodes = {}

        for node in nodes:
            node_id = generate_id()
            self.nodes[node_id] = node

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

    def _apply_rename_node(self, change: AIChange) -> None:
        node_id = change.node_id
        new_text = change.payload.get("to")

        if node_id not in self.nodes:
            return  # safety guard

        if not isinstance(new_text, str):
            return

        self.nodes[node_id].text = new_text

    def _apply_importance(self, change: AIChange) -> None:
        node_id = change.node_id
        new_val = change.payload.get("to")

        if node_id not in self.nodes:
            return

        if not isinstance(new_val, int):
            return

        self.nodes[node_id].importance = new_val

    def _apply_add_node(self, change: AIChange) -> None:
        # Not implemented yet
        return


    def _apply_remove_node(self, change: AIChange) -> None:
        # Not implemented yet
        return


