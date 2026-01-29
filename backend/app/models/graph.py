# graph.py

from pydantic import BaseModel
from typing import List

class Node(BaseModel):
    id: str
    label: str
    importance: int = 1
    type: str = "concept"

class Edge(BaseModel):
    id: str
    from_node: str
    to_node: str
    relation: str

class Graph(BaseModel):
    graph_id: str
    nodes: List[Node]
    edges: List[Edge]
    version: int = 1


