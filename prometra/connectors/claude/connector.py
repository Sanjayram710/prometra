import os
import uuid
import threading
import time
from typing import Dict, Any, Optional

from prometra.connectors.base import BaseConnector
from prometra.connectors.models import ConnectorStatus, ConnectorConfig
from prometra.connectors.claude.models import ClaudeMetadata
from prometra.connectors.events import EventBus, BaseEvent
from prometra.connectors.claude.events import (
    ClaudeConnected, ClaudeDisconnected, 
    ClaudeSessionStarted, ClaudeSessionStopped, 
    ClaudeHealthChanged
)
from prometra.connectors.claude.discovery import ClaudeDiscovery
from prometra.storage.sqlite import SQLiteStorage
from prometra.core.time import utcnow
from prometra.context.builder import ContextBuilder
from prometra.ai.translators import ai_translator_registry

class ClaudeConnector(BaseConnector):
    def __init__(self, event_bus: Optional[EventBus] = None):
        self._config = None
        self._is_connected = False
        self._health_status = ConnectorStatus(state="disconnected")
        self._storage = None
        self._session_thread = None
        self._running = False
        self._event_bus = event_bus

    def set_event_bus(self, event_bus: EventBus):
        self._event_bus = event_bus

    def initialize(self, config: ConnectorConfig) -> None:
        self._config = config
        db_path = os.path.abspath(os.path.join(".prometra", "prometra.db"))
        self._storage = SQLiteStorage(db_path)

    def emit_event(self, event: BaseEvent):
        """Translate event via Generic AI Event Translator and publish to EventBus."""
        generic_event = ai_translator_registry.translate("claude", event)
        if generic_event and self._event_bus:
            self._event_bus.publish(generic_event)
        elif event and self._event_bus:
            self._event_bus.publish(event)

    def connect(self) -> None:
        if not ClaudeDiscovery.is_installed():
            self._is_connected = False
            self._health_status = ConnectorStatus(
                state="error", 
                error_message="Claude Code CLI is not installed or not in PATH."
            )
            return

        self._is_connected = True
        self._health_status = ConnectorStatus(state="connected")
        
        self.emit_event(ClaudeConnected(version=ClaudeDiscovery.get_version() or "1.0.0", executable_path=ClaudeDiscovery.get_executable_path() or ""))
        
        self._running = True
        self._session_thread = threading.Thread(target=self._poll_sessions, daemon=True)
        self._session_thread.start()

    def disconnect(self) -> None:
        self._running = False
        if self._session_thread:
            self._session_thread.join(timeout=2.0)
        
        if self._is_connected:
            self.emit_event(ClaudeDisconnected(reason="Connector disconnected by user"))
            
        self._is_connected = False
        self._health_status = ConnectorStatus(state="disconnected")

    def capture(self, **kwargs) -> Dict[str, Any]:
        """Manually trigger a context capture or session check."""
        if not self._is_connected:
            return {"status": "error", "message": "Not connected"}
            
        builder = ContextBuilder(self._storage)
        project_path = os.path.abspath(".")
        project_id = os.path.basename(project_path)
        ctx = builder.build_context(project_id, project_path)
        
        return {
            "status": "success",
            "context": ctx.model_dump(),
            "metadata": ClaudeDiscovery.get_metadata()
        }

    def _poll_sessions(self):
        """Mock polling for Claude sessions."""
        pass

    def _persist_event(self, event: Any, related_id: str = None):
        """Legacy persist interface redirected to EventBus publishing."""
        self.emit_event(event)

    def metadata(self) -> ClaudeMetadata:
        path = ClaudeDiscovery.get_executable_path() or ""
        version = ClaudeDiscovery.get_version()
        platform_os = ClaudeDiscovery.get_platform()
        
        return ClaudeMetadata(
            name="claude",
            version="1.0.0",
            supported_models=["claude-3-5-sonnet"],
            supported_events=["ClaudeSessionStarted", "ClaudeSessionStopped", "ClaudeHealthChanged", "ClaudePromptSubmitted", "ClaudeResponseReceived"],
            executable_path=path,
            os_platform=platform_os
        )

    def health(self) -> ConnectorStatus:
        if not ClaudeDiscovery.is_installed():
            return ConnectorStatus(state="error", error_message="Claude Code is not installed.")
        return ConnectorStatus(state="connected")

    def supports(self, capability: str) -> bool:
        return capability in ["session_tracking", "context_building", "event_streaming"]

    def shutdown(self) -> None:
        self.disconnect()
        if self._storage:
            self._storage.engine.dispose()
