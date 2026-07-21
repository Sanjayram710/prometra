import os
import uuid
import threading
import time
from typing import Dict, Any

from prometra.connectors.base import BaseConnector
from prometra.connectors.models import ConnectorStatus, ConnectorConfig
from prometra.connectors.claude.models import ClaudeMetadata
from prometra.connectors.claude.events import (
    ClaudeConnected, ClaudeDisconnected, 
    ClaudeSessionStarted, ClaudeSessionStopped, 
    ClaudeHealthChanged
)
from prometra.connectors.claude.discovery import ClaudeDiscovery
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel
from prometra.core.time import utcnow
from prometra.context.builder import ContextBuilder

class ClaudeConnector(BaseConnector):
    def __init__(self):
        self._config = None
        self._is_connected = False
        self._health_status = ConnectorStatus(state="disconnected")
        self._storage = None
        self._session_thread = None
        self._running = False

    def initialize(self, config: ConnectorConfig) -> None:
        self._config = config
        db_path = os.path.abspath(os.path.join(".prometra", "prometra.db"))
        self._storage = SQLiteStorage(db_path)

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
        
        self._running = True
        self._session_thread = threading.Thread(target=self._poll_sessions, daemon=True)
        self._session_thread.start()

    def disconnect(self) -> None:
        self._running = False
        if self._session_thread:
            self._session_thread.join(timeout=2.0)
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
        if not self._storage:
            return
            
        from prometra.ai.translators import ai_translator_registry
        
        generic_event = ai_translator_registry.translate("claude", event)
        if not generic_event:
            return
            
        db = self._storage.get_session()
        try:
            max_seq = db.query(TimelineEventModel).count()
            
            summary = f"{generic_event.event_type} from {generic_event.connector_name}"
            
            tl_event = TimelineEventModel(
                normalized_event_type=generic_event.event_type,
                timestamp=utcnow(),
                sequence=max_seq + 1,
                source="claude_connector",
                summary=summary,
                related_event_ids=[related_id] if related_id else []
            )
            db.add(tl_event)
            db.commit()
        finally:
            db.close()

    def metadata(self) -> ClaudeMetadata:
        path = ClaudeDiscovery.get_executable_path() or ""
        version = ClaudeDiscovery.get_version()
        platform_os = ClaudeDiscovery.get_platform()
        
        return ClaudeMetadata(
            name="claude",
            version="1.0.0",
            supported_models=["claude-3-5-sonnet"],
            supported_events=["ClaudeSessionStarted", "ClaudeSessionStopped", "ClaudeHealthChanged"],
            executable_path=path,
            os_platform=platform_os
        )

    def health(self) -> ConnectorStatus:
        if not ClaudeDiscovery.is_installed():
            return ConnectorStatus(state="error", error_message="Claude Code is not installed.")
        return ConnectorStatus(state="connected")

    def supports(self, capability: str) -> bool:
        return capability in ["session_tracking", "context_building"]

    def shutdown(self) -> None:
        self.disconnect()
        if self._storage:
            self._storage.engine.dispose()
