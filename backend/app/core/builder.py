# Deterministic graph builder

from typing import List
from app.models.input import InputNode

class BuiltGraph:
    def __init__(self, nodes: List[InputNode]):
        self.nodes = nodes
        self.node_count=len(nodes)

def build_graph(nodes: List[InputNode]) -> BuiltGraph:
    return BuiltGraph(nodes)