from typing import Literal, Optional
from pydantic import BaseModel


class AIChange(BaseModel):
    type: Literal["importance", "add_node", "remove_node", "rename_node"]
    node_id: Optional[str]
    payload: dict
