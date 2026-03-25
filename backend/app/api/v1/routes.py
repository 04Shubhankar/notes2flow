from fastapi import APIRouter, HTTPException

from app.models.input import ParseRequest
from app.core.pipeline import run_pipeline
from app.ai.reviewer import refine_graph

router = APIRouter()

@router.post("/graph/parse")
def parse_graph(request: ParseRequest):
    print("Received nodes:", len(request.nodes))
    for n in request.nodes:
        print("-", n.text)
    try:
        graph, corrections = run_pipeline([n.model_dump() for n in request.nodes])
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    if request.ai_review:
        graph = refine_graph(graph)

    return {
    "graph": {
        "nodes": [
            {
                "id": node.id,
                "label": node.label,
                "importance": node.importance
            }
            for node in graph.nodes
        ],
        "edges": [
            {
                "id": edge.id,
                "source": edge.from_node,
                "target": edge.to_node
            }
            for edge in graph.edges
        ]
    },
    "meta": {
        "version": graph.version,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "corrections": corrections
    }
}
