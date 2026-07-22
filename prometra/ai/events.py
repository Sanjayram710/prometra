from pydantic import Field
from typing import Optional, Dict, Any, List
from prometra.connectors.events import BaseEvent
from prometra.ai.models import TokenCount, ToolCall, PromptData

class AiEvent(BaseEvent):
    """Base class for all provider-agnostic AI events."""
    event_type: str = "AiEvent"
    connector_name: str = "ai"
    session_id: str = "system"
    model_name: Optional[str] = None
    prompt_id: Optional[str] = None
    tool_name: Optional[str] = None
    cost: float = 0.0
    tokens: Optional[TokenCount] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_description(self) -> str:
        return f"{self.event_type} from {self.connector_name}"

class SessionStarted(AiEvent):
    event_type: str = "SessionStarted"
    project_path: Optional[str] = None

    def get_description(self) -> str:
        return f"AI Session Started for project {self.project_path or self.session_id}"

class SessionEnded(AiEvent):
    event_type: str = "SessionEnded"
    duration_seconds: int = 0

    def get_description(self) -> str:
        return f"AI Session Ended (Duration: {self.duration_seconds}s)"

class PromptSubmitted(AiEvent):
    event_type: str = "PromptSubmitted"
    prompt: Optional[PromptData] = None
    content: Optional[str] = None

    def get_description(self) -> str:
        text = self.content or (self.prompt.content if self.prompt else "")
        truncated = f'"{text[:60]}..."' if len(text) > 60 else f'"{text}"'
        return f"Prompt Submitted: {truncated}"

class PromptUpdated(AiEvent):
    event_type: str = "PromptUpdated"
    content: str = ""

    def get_description(self) -> str:
        return f"Prompt Updated: {self.content[:60]}"

class ResponseStarted(AiEvent):
    event_type: str = "ResponseStarted"
    model: Optional[str] = None

    def get_description(self) -> str:
        return f"Response Started ({self.model or self.model_name or 'AI'})"

class ResponseReceived(AiEvent):
    event_type: str = "ResponseReceived"
    content: str = ""
    model: Optional[str] = None

    def get_description(self) -> str:
        truncated = f'"{self.content[:60]}..."' if len(self.content) > 60 else f'"{self.content}"'
        return f"Response Received: {truncated}"

class ResponseCompleted(AiEvent):
    event_type: str = "ResponseCompleted"
    response_time_ms: int = 0

    def get_description(self) -> str:
        return f"Response Completed in {self.response_time_ms}ms"

class ToolInvocationStarted(AiEvent):
    event_type: str = "ToolInvocationStarted"
    tool_name: str = ""

    def get_description(self) -> str:
        return f"Tool Invocation Started: {self.tool_name}"

class ToolInvocationCompleted(AiEvent):
    event_type: str = "ToolInvocationCompleted"
    tool_name: str = ""
    result_summary: Optional[str] = None

    def get_description(self) -> str:
        return f"Tool Invocation Completed: {self.tool_name}"

class ToolInvocationFailed(AiEvent):
    event_type: str = "ToolInvocationFailed"
    tool_name: str = ""
    error_message: str = ""

    def get_description(self) -> str:
        return f"Tool Invocation Failed: {self.tool_name} - {self.error_message}"

class ToolInvocation(AiEvent):
    event_type: str = "ToolInvocation"
    tool: Optional[ToolCall] = None

    def get_description(self) -> str:
        name = self.tool_name or (self.tool.tool_name if self.tool else "Tool")
        return f"Tool Invocation: {name}"

class TokenUsage(AiEvent):
    event_type: str = "TokenUsage"

    def get_description(self) -> str:
        total = self.tokens.total_tokens if self.tokens else 0
        return f"Token Usage: {total} total tokens"

class CostRecorded(AiEvent):
    event_type: str = "CostRecorded"

    def get_description(self) -> str:
        return f"Cost Recorded: ${self.cost:.4f}"

class ModelChanged(AiEvent):
    event_type: str = "ModelChanged"
    new_model: str = ""

    def get_description(self) -> str:
        return f"Model Changed to {self.new_model}"

class ModelSelected(AiEvent):
    event_type: str = "ModelSelected"
    model_name: str = ""
    provider: str = ""

    def get_description(self) -> str:
        return f"Model Selected: {self.model_name} ({self.provider})"

class ContextInjected(AiEvent):
    event_type: str = "ContextInjected"
    context_summary: str = ""
    files_count: int = 0

    def get_description(self) -> str:
        return f"Context Injected: {self.files_count} files"

class ContextBuilt(AiEvent):
    event_type: str = "ContextBuilt"
    summary: str = ""
    num_files_included: int = 0

    def get_description(self) -> str:
        return f"Context Built: {self.num_files_included} files included"

class ErrorOccurred(AiEvent):
    event_type: str = "ErrorOccurred"
    error_message: str = ""
    severity: str = "error"

    def get_description(self) -> str:
        return f"Error Occurred: {self.error_message}"

class RetryAttempt(AiEvent):
    event_type: str = "RetryAttempt"
    attempt_number: int = 1
    reason: str = ""

    def get_description(self) -> str:
        return f"Retry Attempt #{self.attempt_number}: {self.reason}"

class ConnectorConnected(AiEvent):
    event_type: str = "ConnectorConnected"

    def get_description(self) -> str:
        return f"Connector Connected: {self.connector_name}"

class ConnectorDisconnected(AiEvent):
    event_type: str = "ConnectorDisconnected"
    reason: str = ""

    def get_description(self) -> str:
        return f"Connector Disconnected: {self.connector_name} ({self.reason})"

class LatencyMeasured(AiEvent):
    event_type: str = "LatencyMeasured"
    latency_ms: int = 0
    operation: str = ""

    def get_description(self) -> str:
        return f"Latency Measured: {self.operation} {self.latency_ms}ms"
