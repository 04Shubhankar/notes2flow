# Apply AI proposals safely

from app.models.graph import Graph

def diff_graphs(old_graph:Graph, new_graph: Graph):
    old_nodes={node.text: node for node in old_graph.nodes}
    new_nodes = {node.text: node for node in new_graph.nodes}
    
    diff = {
        "added": [],
        "removed": [],
        "changed": []
    }

    for text,node in new_nodes.items():
        if text not in old_nodes:
            diff["added"].append({
            "text": node.text,
            "importance": node.importance
        })
            
    for text,node in old_nodes.items():
        if text not in new_nodes:
            diff["removed"].append({
            "text": node.text,
            "importance": node.importance
        })

    for text, old_node in old_nodes.items():
        if text in new_nodes:
            new_node = new_nodes[text]
            if old_node.importance != new_node.importance:
                diff["changed"].append({
                    "text": text,
                    "from_importance": old_node.importance,
                    "to_importance": new_node.importance
                })

    return diff