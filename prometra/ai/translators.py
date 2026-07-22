from typing import Optional
from prometra.connectors.events import BaseEvent
from prometra.ai.models import TokenCount, ToolCall, PromptData
import prometra.ai.events as ai_ev
import prometra.connectors.claude.events as cl_ev

class EventTranslatorRegistry:
    def __init__(self):
        self.translators = {}
        
    def register(self, connector_name: str, translator_func):
        self.translators[connector_name] = translator_func
        
    def translate(self, connector_name: str, event: BaseEvent) -> Optional[ai_ev.AiEvent]:
        # If event is already an AiEvent, return it directly
        if isinstance(event, ai_ev.AiEvent):
            return event

        translator = self.translators.get(connector_name)
        if translator:
            return translator(event)
        return None

def claude_event_translator(event: BaseEvent) -> Optional[ai_ev.AiEvent]:
    if isinstance(event, cl_ev.ClaudeSessionStarted):
        return ai_ev.SessionStarted(
            connector_name="claude",
            session_id=event.session_id,
            project_path=event.project_path
        )
    elif isinstance(event, cl_ev.ClaudeSessionStopped):
        return ai_ev.SessionEnded(
            connector_name="claude",
            session_id=event.session_id,
            duration_seconds=event.duration_seconds
        )
    elif isinstance(event, cl_ev.ClaudePromptSubmitted):
        return ai_ev.PromptSubmitted(
            connector_name="claude",
            session_id=event.session_id,
            content=event.content,
            prompt_id=event.prompt_id,
            model_name=event.model_name,
            prompt=PromptData(content=event.content)
        )
    elif isinstance(event, cl_ev.ClaudePromptUpdated):
        return ai_ev.PromptUpdated(
            connector_name="claude",
            session_id=event.session_id,
            content=event.content
        )
    elif isinstance(event, cl_ev.ClaudeResponseStarted):
        return ai_ev.ResponseStarted(
            connector_name="claude",
            session_id=event.session_id,
            model=event.model_name,
            model_name=event.model_name
        )
    elif isinstance(event, cl_ev.ClaudeResponseReceived):
        tokens = TokenCount(
            prompt_tokens=event.prompt_tokens,
            completion_tokens=event.completion_tokens,
            total_tokens=event.prompt_tokens + event.completion_tokens
        )
        return ai_ev.ResponseReceived(
            connector_name="claude",
            session_id=event.session_id,
            content=event.content,
            model=event.model_name,
            model_name=event.model_name,
            cost=event.cost,
            tokens=tokens
        )
    elif isinstance(event, cl_ev.ClaudeResponseCompleted):
        return ai_ev.ResponseCompleted(
            connector_name="claude",
            session_id=event.session_id,
            response_time_ms=event.response_time_ms
        )
    elif isinstance(event, cl_ev.ClaudeToolInvocationStarted):
        return ai_ev.ToolInvocationStarted(
            connector_name="claude",
            session_id=event.session_id,
            tool_name=event.tool_name
        )
    elif isinstance(event, cl_ev.ClaudeToolInvocationCompleted):
        return ai_ev.ToolInvocationCompleted(
            connector_name="claude",
            session_id=event.session_id,
            tool_name=event.tool_name,
            result_summary=event.result_summary
        )
    elif isinstance(event, cl_ev.ClaudeToolInvocationFailed):
        return ai_ev.ToolInvocationFailed(
            connector_name="claude",
            session_id=event.session_id,
            tool_name=event.tool_name,
            error_message=event.error_message
        )
    elif isinstance(event, cl_ev.ClaudeTokenUsage):
        tokens = TokenCount(
            prompt_tokens=event.prompt_tokens,
            completion_tokens=event.completion_tokens,
            total_tokens=event.total_tokens or (event.prompt_tokens + event.completion_tokens)
        )
        return ai_ev.TokenUsage(
            connector_name="claude",
            session_id=event.session_id,
            tokens=tokens
        )
    elif isinstance(event, cl_ev.ClaudeCostRecorded):
        return ai_ev.CostRecorded(
            connector_name="claude",
            session_id=event.session_id,
            cost=event.cost
        )
    elif isinstance(event, cl_ev.ClaudeModelChanged):
        return ai_ev.ModelChanged(
            connector_name="claude",
            session_id=event.session_id,
            new_model=event.new_model
        )
    elif isinstance(event, cl_ev.ClaudeContextInjected):
        return ai_ev.ContextInjected(
            connector_name="claude",
            session_id=event.session_id,
            context_summary=event.context_summary,
            files_count=event.files_count
        )
    elif isinstance(event, cl_ev.ClaudeErrorOccurred):
        return ai_ev.ErrorOccurred(
            connector_name="claude",
            session_id=event.session_id,
            error_message=event.error_message,
            severity=event.severity
        )
    elif isinstance(event, cl_ev.ClaudeRetryAttempt):
        return ai_ev.RetryAttempt(
            connector_name="claude",
            session_id=event.session_id,
            attempt_number=event.attempt_number,
            reason=event.reason
        )
    elif isinstance(event, cl_ev.ClaudeConnected):
        return ai_ev.ConnectorConnected(
            connector_name="claude",
            session_id="system"
        )
    elif isinstance(event, cl_ev.ClaudeDisconnected):
        return ai_ev.ConnectorDisconnected(
            connector_name="claude",
            session_id="system",
            reason=event.reason
        )
    elif isinstance(event, cl_ev.ClaudeHealthChanged):
        if not event.is_healthy:
            return ai_ev.ErrorOccurred(
                connector_name="claude",
                session_id="system",
                error_message=event.status_message,
                severity="error"
            )
    return None

# Global registry
ai_translator_registry = EventTranslatorRegistry()
ai_translator_registry.register("claude", claude_event_translator)
