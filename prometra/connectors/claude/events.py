from typing import Any

from pydantic import Field

from prometra.connectors.events import BaseEvent


class ClaudeConnected(BaseEvent):
    event_type: str = "ClaudeConnected"
    version: str = "1.0.0"
    executable_path: str = ""


class ClaudeDisconnected(BaseEvent):
    event_type: str = "ClaudeDisconnected"
    reason: str = ""


class ClaudeSessionStarted(BaseEvent):
    event_type: str = "ClaudeSessionStarted"
    session_id: str
    project_path: str


class ClaudeSessionStopped(BaseEvent):
    event_type: str = "ClaudeSessionStopped"
    session_id: str
    duration_seconds: int


class ClaudeHealthChanged(BaseEvent):
    event_type: str = "ClaudeHealthChanged"
    is_healthy: bool
    status_message: str


class ClaudePromptSubmitted(BaseEvent):
    event_type: str = "ClaudePromptSubmitted"
    session_id: str
    content: str
    prompt_id: str | None = None
    model_name: str | None = "claude-3-5-sonnet"


class ClaudePromptUpdated(BaseEvent):
    event_type: str = "ClaudePromptUpdated"
    session_id: str
    content: str


class ClaudeResponseStarted(BaseEvent):
    event_type: str = "ClaudeResponseStarted"
    session_id: str
    model_name: str = "claude-3-5-sonnet"


class ClaudeResponseReceived(BaseEvent):
    event_type: str = "ClaudeResponseReceived"
    session_id: str
    content: str
    model_name: str = "claude-3-5-sonnet"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0


class ClaudeResponseCompleted(BaseEvent):
    event_type: str = "ClaudeResponseCompleted"
    session_id: str
    response_time_ms: int = 0


class ClaudeToolInvocationStarted(BaseEvent):
    event_type: str = "ClaudeToolInvocationStarted"
    session_id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ClaudeToolInvocationCompleted(BaseEvent):
    event_type: str = "ClaudeToolInvocationCompleted"
    session_id: str
    tool_name: str
    result_summary: str | None = None


class ClaudeToolInvocationFailed(BaseEvent):
    event_type: str = "ClaudeToolInvocationFailed"
    session_id: str
    tool_name: str
    error_message: str


class ClaudeTokenUsage(BaseEvent):
    event_type: str = "ClaudeTokenUsage"
    session_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ClaudeCostRecorded(BaseEvent):
    event_type: str = "ClaudeCostRecorded"
    session_id: str
    cost: float = 0.0


class ClaudeModelChanged(BaseEvent):
    event_type: str = "ClaudeModelChanged"
    session_id: str
    new_model: str


class ClaudeContextInjected(BaseEvent):
    event_type: str = "ClaudeContextInjected"
    session_id: str
    context_summary: str = ""
    files_count: int = 0


class ClaudeErrorOccurred(BaseEvent):
    event_type: str = "ClaudeErrorOccurred"
    session_id: str
    error_message: str
    severity: str = "error"


class ClaudeRetryAttempt(BaseEvent):
    event_type: str = "ClaudeRetryAttempt"
    session_id: str
    attempt_number: int = 1
    reason: str = ""
