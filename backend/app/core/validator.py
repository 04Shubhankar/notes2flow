# Graph + AI rule enforcement

from app.models.input import InputNode

class ValidationError(Exception):
    pass

def validate(nodes):
    validate_basics(nodes)
    validate_graph(nodes)
    validate_semantics(nodes)

def validate_basics(nodes):
    if not isinstance(nodes,list):
        raise ValidationError("Input Must be a List of Nodes")
    
    if not nodes:
        raise ValidationError("Input List Cannot be empty")
    
    for idx,node in enumerate(nodes):
        if not isinstance(node,InputNode):
            raise ValidationError(
                f"Item as index {idx} is not an InputNode"
            )  
        
def validate_graph(nodes):
    seen = set()

    for idx, node in enumerate(nodes):
        if node.text in seen:
            raise ValidationError(
                f"Duplicate node text at index {idx}: '{node.text}'"
            )
        seen.add(node.text)
       

def validate_semantics(nodes):
    for idx,node in enumerate(nodes):
        text_length = len(node.text)

        if text_length<3:
            raise ValidationError(
                f"Node {idx}: text too short to be meaningful"
            )
      
        if node.importance >= 4 and text_length < 10:
            raise ValidationError(
                f"Node {idx}: high importance with very short text"
            )