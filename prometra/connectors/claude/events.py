from prometra.connectors.events import BaseEvent

class ClaudeConnected(BaseEvent):
    event_type: str = "ClaudeConnected"
    version: str
    executable_path: str
    
class ClaudeDisconnected(BaseEvent):
    event_type: str = "ClaudeDisconnected"
    reason: str
    
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
