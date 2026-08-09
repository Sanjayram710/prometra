from prometra.ai.events import (
    ErrorOccurred,
    LatencyMeasured,
    SessionStarted,
    TokenUsage,
    ToolInvocation,
)
from prometra.ai.metrics import AiMetricsAggregator
from prometra.ai.models import TokenCount, ToolCall
from prometra.ai.translators import ai_translator_registry
from prometra.connectors.claude.events import ClaudeHealthChanged, ClaudeSessionStarted


def test_claude_translation():
    claude_event = ClaudeSessionStarted(session_id="123", project_path="/test")
    generic = ai_translator_registry.translate("claude", claude_event)
    assert generic is not None
    assert isinstance(generic, SessionStarted)
    assert generic.session_id == "123"
    assert generic.connector_name == "claude"


def test_claude_health_translation():
    healthy = ClaudeHealthChanged(is_healthy=True, status_message="OK")
    unhealthy = ClaudeHealthChanged(is_healthy=False, status_message="Error")

    assert ai_translator_registry.translate("claude", healthy) is None

    gen_unhealthy = ai_translator_registry.translate("claude", unhealthy)
    assert isinstance(gen_unhealthy, ErrorOccurred)
    assert gen_unhealthy.error_message == "Error"


def test_metrics_aggregator():
    events = [
        TokenUsage(
            connector_name="test",
            session_id="1",
            tokens=TokenCount(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        ),
        LatencyMeasured(
            connector_name="test",
            session_id="1",
            latency_ms=100,
            operation="completion",
        ),
        LatencyMeasured(
            connector_name="test",
            session_id="1",
            latency_ms=200,
            operation="completion",
        ),
        ToolInvocation(
            connector_name="test",
            session_id="1",
            tool=ToolCall(tool_name="test_tool", arguments={}),
        ),
    ]

    metrics = AiMetricsAggregator.aggregate(events)
    assert metrics["total_prompt_tokens"] == 10
    assert metrics["total_completion_tokens"] == 20
    assert metrics["average_latency_ms"] == 150
    assert metrics["tool_invocation_frequencies"]["test_tool"] == 1
