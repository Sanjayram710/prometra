from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class TokenCount(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None

class PromptData(BaseModel):
    content: str
    role: str = "user"
    context_files: List[str] = Field(default_factory=list)
