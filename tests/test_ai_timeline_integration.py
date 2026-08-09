import os
import tempfile

import pytest
from typer.testing import CliRunner

import prometra.connectors.claude.events as cl_ev
from prometra.cli.main import app
from prometra.connectors.claude.connector import ClaudeConnector
from prometra.connectors.events import EventBus
from prometra.storage.models import AiEventModel, TimelineEventModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter

runner = CliRunner()


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_ai_prometra.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()


@pytest.fixture
def ai_environment(temp_db):
    event_bus = EventBus()
    timeline_engine = TimelineEngine(temp_db, event_bus=event_bus)
    connector = ClaudeConnector(event_bus=event_bus)
    return {
        "storage": temp_db,
        "event_bus": event_bus,
        "timeline_engine": timeline_engine,
        "connector": connector,
    }


def test_claude_prompt_and_response_pipeline(ai_environment):
    connector = ai_environment["connector"]
    storage = ai_environment["storage"]

    # Emit Prompt Submitted
    prompt_ev = cl_ev.ClaudePromptSubmitted(
        session_id="sess-ai-1",
        content="Create JWT authentication middleware",
        model_name="claude-3-5-sonnet",
    )
    connector.emit_event(prompt_ev)

    # Emit Response Received
    resp_ev = cl_ev.ClaudeResponseReceived(
        session_id="sess-ai-1",
        content="Generated authentication middleware",
        model_name="claude-3-5-sonnet",
        prompt_tokens=150,
        completion_tokens=300,
        cost=0.0045,
    )
    connector.emit_event(resp_ev)

    # Verify SQLite Database persistence
    db = storage.get_session()
    ai_records = db.query(AiEventModel).all()
    tl_records = db.query(TimelineEventModel).all()
    db.close()

    assert len(ai_records) == 2
    assert len(tl_records) == 2

    types = [r.event_type for r in ai_records]
    assert "PromptSubmitted" in types
    assert "ResponseReceived" in types

    # Verify description formatting
    descriptions = [r.description for r in ai_records]
    assert any("Prompt Submitted" in d for d in descriptions)
    assert any("Response Received" in d for d in descriptions)


def test_claude_tool_invocation_pipeline(ai_environment):
    connector = ai_environment["connector"]
    engine = ai_environment["timeline_engine"]

    start_tool = cl_ev.ClaudeToolInvocationStarted(
        session_id="sess-ai-1",
        tool_name="Read File",
        arguments={"path": "backend/auth.py"},
    )
    connector.emit_event(start_tool)

    complete_tool = cl_ev.ClaudeToolInvocationCompleted(
        session_id="sess-ai-1", tool_name="Read File", result_summary="Read 50 lines"
    )
    connector.emit_event(complete_tool)

    events = engine.get_events(session_id="sess-ai-1")
    assert len(events) == 2
    summaries = [e.summary for e in events]
    assert any("Tool Invocation Started: Read File" in s for s in summaries)
    assert any("Tool Invocation Completed: Read File" in s for s in summaries)


def test_claude_token_and_cost_and_error(ai_environment):
    connector = ai_environment["connector"]
    engine = ai_environment["timeline_engine"]

    token_ev = cl_ev.ClaudeTokenUsage(
        session_id="sess-ai-2",
        prompt_tokens=500,
        completion_tokens=250,
        total_tokens=750,
    )
    connector.emit_event(token_ev)

    cost_ev = cl_ev.ClaudeCostRecorded(session_id="sess-ai-2", cost=0.0125)
    connector.emit_event(cost_ev)

    err_ev = cl_ev.ClaudeErrorOccurred(
        session_id="sess-ai-2",
        error_message="API rate limit exceeded",
        severity="error",
    )
    connector.emit_event(err_ev)

    summary = engine.get_summary(TimelineFilter(session_id="sess-ai-2"))
    assert summary.total_events == 3
    assert summary.total_tokens == 750
    assert summary.estimated_cost == 0.0125


def test_connector_connected_and_disconnected(ai_environment):
    connector = ai_environment["connector"]
    engine = ai_environment["timeline_engine"]

    conn_ev = cl_ev.ClaudeConnected(
        version="1.0.0", executable_path="/usr/local/bin/claude"
    )
    connector.emit_event(conn_ev)

    disc_ev = cl_ev.ClaudeDisconnected(reason="User initiated shutdown")
    connector.emit_event(disc_ev)

    events = engine.get_events()
    assert len(events) == 2
    summaries = [e.summary for e in events]
    assert any("Connector Connected: claude" in s for s in summaries)
    assert any("Connector Disconnected: claude" in s for s in summaries)


def test_timeline_cli_ai_filtering_and_search(monkeypatch, ai_environment):
    connector = ai_environment["connector"]
    storage = ai_environment["storage"]

    # Emit events
    connector.emit_event(
        cl_ev.ClaudePromptSubmitted(
            session_id="sess-cli", content="Refactor JWT authentication module"
        )
    )
    connector.emit_event(
        cl_ev.ClaudeResponseReceived(
            session_id="sess-cli",
            content="Refactored JWT module successfully",
            prompt_tokens=100,
            completion_tokens=100,
        )
    )
    connector.emit_event(
        cl_ev.ClaudeToolInvocationStarted(
            session_id="sess-cli", tool_name="Write File", arguments={"path": "auth.py"}
        )
    )

    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: storage)

    # Test --type ai
    res_ai = runner.invoke(app, ["timeline", "--type", "ai"])
    assert res_ai.exit_code == 0
    assert "PromptSubmitted" in res_ai.stdout or "Prompt Submitted" in res_ai.stdout

    # Test --connector claude
    res_conn = runner.invoke(app, ["timeline", "--connector", "claude"])
    assert res_conn.exit_code == 0
    assert "claude" in res_conn.stdout

    # Test --search prompt
    res_search_prompt = runner.invoke(app, ["timeline", "--search", "prompt"])
    assert res_search_prompt.exit_code == 0
    assert (
        "PromptSubmitted" in res_search_prompt.stdout
        or "Prompt Submitted" in res_search_prompt.stdout
    )

    # Test --search tool
    res_search_tool = runner.invoke(app, ["timeline", "--search", "tool"])
    assert res_search_tool.exit_code == 0
    assert (
        "ToolInvocation" in res_search_tool.stdout
        or "Tool Invocation" in res_search_tool.stdout
    )

    # Test --summary
    res_summary = runner.invoke(app, ["timeline", "--summary"])
    assert res_summary.exit_code == 0
    assert "AI Prompts" in res_summary.stdout
    assert "AI Responses" in res_summary.stdout
    assert "Tool Calls" in res_summary.stdout
