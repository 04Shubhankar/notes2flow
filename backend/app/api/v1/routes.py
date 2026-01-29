from fastapi import APIRouter

from app.models.input import ParseRequest
from app.core.builder import build_graph

router = APIRouter()

@router.post("/graph/parse")
def parse_graph(request:ParseRequest):
    graph = build_graph(request.nodes)
    return{
        "graph":graph,
        "meta":{
            "version":graph.version,
            "node_count":len(graph.nodes)
        }
    }
