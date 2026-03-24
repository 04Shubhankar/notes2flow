from pydantic import BaseModel, Field
from typing import List, Optional

class InputNode(BaseModel):
    text: str = Field(..., min_length=1, description="Content typed by the user")
    importance: int = Field(..., ge=1, description="User-defined importance, ≥1")
    parent_id: Optional[str] = Field(None, description="Optional parent node ID for hierarchy")

class ParseRequest(BaseModel):
    nodes: List[InputNode] = Field(..., description="List of user input nodes")
    ai_review: bool = Field(default=False, description="Whether to request AI review")