from typing import List, Dict
from app.models.input import InputNode
from app.models.ai import AIChange
from app.utils.ids import generate_id
from app.models.graph import Graph, Node, Edge


def build_graph(input_nodes: List[InputNode]) -> Graph:
    nodes: List[Node] = []
    edges: List[Edge] = []

    stack = []

    for inp in input_nodes:
        node_id = generate_id()

        node = Node(
            id=node_id,
            label=inp.text,
            importance=inp.importance,
            type="concept"
        )

        nodes.append(node)

        # remove nodes that are same importance or less important (lower number)
        while stack and stack[-1]["importance"] <= inp.importance:
            stack.pop()

        # connect to nearest valid parent (which is more important)
        if stack:
            edges.append(
                Edge(
                    id=generate_id(),
                    from_node=stack[-1]["id"],
                    to_node=node_id,
                    relation="hierarchy"
                )
            )

        stack.append({
            "id": node_id,
            "importance": inp.importance
        })

    return Graph(
        graph_id=generate_id(),
        nodes=nodes,
        edges=edges,
        version=1
    )

