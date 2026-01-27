from app.core.normalizer import normalize_input
from app.core.validator import validate
from app.core.builder import build_graph

def run_pipeline(raw_nodes):
    normalized , corrections = normalize_input(raw_nodes)
    validate(normalized)
    graph = build_graph(normalized)
    return graph,corrections



"""
Usage:
from app.core.pipeline import run_pipeline

graph, corrections = run_pipeline(payload)
"""