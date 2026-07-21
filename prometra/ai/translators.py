from typing import Optional
from prometra.connectors.events import BaseEvent
from prometra.ai.events import AiEvent, SessionStarted, SessionEnded, ErrorOccurred
from prometra.connectors.claude.events import ClaudeSessionStarted, ClaudeSessionStopped, ClaudeHealthChanged

class EventTranslatorRegistry:
    def __init__(self):
        self.translators = {}
        
    def register(self, connector_name: str, translator_func):
        self.translators[connector_name] = translator_func
        
    def translate(self, connector_name: str, event: BaseEvent) -> Optional[AiEvent]:
        translator = self.translators.get(connector_name)
        if translator:
            return translator(event)
        return None

def claude_event_translator(event: BaseEvent) -> Optional[AiEvent]:
    if isinstance(event, ClaudeSessionStarted):
        return SessionStarted(
            connector_name="claude",
            session_id=event.session_id,
            project_path=event.project_path
        )
    elif isinstance(event, ClaudeSessionStopped):
        return SessionEnded(
            connector_name="claude",
            session_id=event.session_id,
            duration_seconds=event.duration_seconds
        )
    elif isinstance(event, ClaudeHealthChanged):
        if not event.is_healthy:
            return ErrorOccurred(
                connector_name="claude",
                session_id="system",
                error_message=event.status_message,
                severity="error"
            )
    return None

# Global registry
ai_translator_registry = EventTranslatorRegistry()
ai_translator_registry.register("claude", claude_event_translator)
