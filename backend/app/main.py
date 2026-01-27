from app.core.normalizer import normalize_input
from app.core.builder import BuiltGraph
from app.ai.reviewer import refine_graph
from app.ai.reviewer import serialize_graph


def main():
    # Raw input (frontend-style)
    raw_nodes = [
        {
            "id": "1",
            "text": "Photosynthesis",
            "importance": 5,
            "parent_id": None,
        },
        {
            "id": "2",
            "text": "Light Reactions",
            "importance": 3,
            "parent_id": "1",
        },
        {
            "id": "3",
            "text": "Calvin Cycle",
            "importance": 2,
            "parent_id": "1",
        },
    ]


    #  Step 1: normalize raw input → InputNode objects
    normalized_nodes, corrections = normalize_input(raw_nodes)

    if corrections:
        print("Input corrections applied:")
        for c in corrections:
            print(c)

    #  Step 2: build graph correctly
    graph = BuiltGraph(normalized_nodes)

    print("\n===== BEFORE AI REVIEW =====")
    print(serialize_graph(graph))

    #  Step 3: AI refinement
    graph = refine_graph(graph)

    print("\n===== AFTER AI REVIEW =====")
    print(serialize_graph(graph))


if __name__ == "__main__":
    main()
