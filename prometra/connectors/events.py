from typing import Callable, Dict, List, Type, Any
from pydantic import BaseModel
import threading
from prometra.core.time import utcnow

class BaseEvent(BaseModel):
    event_type: str
    timestamp: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if not self.timestamp:
            self.timestamp = str(utcnow())

class SessionStarted(BaseEvent):
    event_type: str = "SessionStarted"
    session_id: str
    project_id: str

class SessionStopped(BaseEvent):
    event_type: str = "SessionStopped"
    session_id: str
    duration_seconds: int

class FilesystemChanged(BaseEvent):
    event_type: str = "FilesystemChanged"
    path: str
    operation: str

class GitCommit(BaseEvent):
    event_type: str = "GitCommit"
    commit_id: str
    branch: str

class GitBranchChanged(BaseEvent):
    event_type: str = "GitBranchChanged"
    old_branch: str
    new_branch: str

class AnalysisCompleted(BaseEvent):
    event_type: str = "AnalysisCompleted"
    project_id: str
    score: float

class ReportGenerated(BaseEvent):
    event_type: str = "ReportGenerated"
    project_id: str
    formats: List[str]

class ConnectorConnected(BaseEvent):
    event_type: str = "ConnectorConnected"
    connector_name: str

class ConnectorDisconnected(BaseEvent):
    event_type: str = "ConnectorDisconnected"
    connector_name: str

class ContextBuilt(BaseEvent):
    event_type: str = "ContextBuilt"
    context_id: str

class EventBus:
    """Publish/Subscribe Event Bus"""
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[BaseEvent], None]]] = {}
        self._generic_subscribers: List[Callable[[BaseEvent], None]] = []
        self._lock = threading.Lock()

    def subscribe(self, event_class_or_type: Any, callback: Callable[[BaseEvent], None]):
        with self._lock:
            if event_class_or_type == "*" or event_class_or_type is BaseEvent:
                self._generic_subscribers.append(callback)
            elif isinstance(event_class_or_type, str):
                if event_class_or_type not in self._subscribers:
                    self._subscribers[event_class_or_type] = []
                self._subscribers[event_class_or_type].append(callback)
            elif hasattr(event_class_or_type, "model_fields") and "event_type" in event_class_or_type.model_fields:
                event_type = event_class_or_type.model_fields['event_type'].default
                if event_type not in self._subscribers:
                    self._subscribers[event_type] = []
                self._subscribers[event_type].append(callback)
            else:
                self._generic_subscribers.append(callback)

    def publish(self, event: BaseEvent):
        with self._lock:
            subs = self._subscribers.get(event.event_type, []).copy()
            generics = self._generic_subscribers.copy()
            
        for callback in subs + generics:
            try:
                callback(event)
            except Exception:
                pass

