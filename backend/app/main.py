from app.core.pipeline import run_pipeline
from app.core.validator import ValidationError

raw_nodes = [
    {"text": "Learn Python", "importance": "3"},
    {"text": "Write unit tests", "importance": "4"},
    {"text": "Refactor codebase", "importance": 2},
    {"text": "Add CI pipeline", "importance": "5"},
    {"text": "Document API", "importance": None},
    {"text": "Optimize", "importance": -1},
    {"text": "ok", "importance": 1},
]

try:
    graph, corrections = run_pipeline(raw_nodes)

    print("Nodes:")
    for node in graph.nodes:
        print(node.text, node.importance)

    print("\nCorrections:")
    print(corrections)

except ValidationError as e:
    print("❌ Validation failed")
    print(str(e))
