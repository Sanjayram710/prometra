from pydantic import Field
from typing import Optional, Dict, Any, List
from prometra.connectors.events import BaseEvent
from prometra.ai.models import TokenCount, ToolCall, PromptData

class AiEvent(BaseEvent):
    """Base class for all provider-agnostic AI events."""
    event_type: str = "AiEvent"
    connector_name: str
    session_id: str

class PromptSubmitted(AiEvent):
    event_type: str = "PromptSubmitted"
    prompt: PromptData

class ResponseReceived(AiEvent):
    event_type: str = "ResponseReceived"
    content: str
    model: str
    tokens: Optional[TokenCount] = None

class ToolInvocation(AiEvent):
    event_type: str = "ToolInvocation"
    tool: ToolCall

class ModelSelected(AiEvent):
    event_type: str = "ModelSelected"
    model_name: str
    provider: str

class ContextBuilt(AiEvent):
    event_type: str = "ContextBuilt"
    summary: str
    num_files_included: int

class TokenUsage(AiEvent):
    event_type: str = "TokenUsage"
    tokens: TokenCount

class LatencyMeasured(AiEvent):
    event_type: str = "LatencyMeasured"
    latency_ms: int
    operation: str

class SessionStarted(AiEvent):
    event_type: str = "SessionStarted"
    project_path: str

class SessionEnded(AiEvent):
    event_type: str = "SessionEnded"
    duration_seconds: int

class ErrorOccurred(AiEvent):
    event_type: str = "ErrorOccurred"
    error_message: str
    severity: str = "error"
