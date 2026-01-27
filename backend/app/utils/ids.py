# UUID helpers

import uuid


def generate_id() -> str:
    """
    Generate a unique ID for graph nodes.
    """
    return str(uuid.uuid4())
