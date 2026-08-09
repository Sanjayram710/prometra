from typing import Any

from pydantic import BaseModel, Field


class TokenCount(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    result: str | None = None


class PromptData(BaseModel):
    content: str
    role: str = "user"
    context_files: list[str] = Field(default_factory=list)
