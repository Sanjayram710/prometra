import datetime
import os
import tempfile

import pytest
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.core.time import utcnow
from prometra.replay.engine import ReplayEngine
from prometra.replay.exporter import ReplayExporter
from prometra.replay.formatter import ReplayFormatter
from prometra.replay.player import ReplayPlayer
from prometra.storage.models import SessionModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine

runner = CliRunner()


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_replay.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()


@pytest.fixture
def populated_session_engine(temp_db):
    engine = TimelineEngine(temp_db)
    now = utcnow()

    # Create SessionModel
    db = temp_db.get_session()
    sess = SessionModel(
        session_id="sess-replay-100",
        project_id="test_project",
        start_ts=now - datetime.timedelta(minutes=20),
        end_ts=now,
        duration_seconds=1200,
        project_path="/app",
        working_directory="/app",
        status="completed",
    )
    db.add(sess)
    db.commit()
    db.close()

    # Session events sequence
    engine.append_event(
        {
            "type": "session",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=20),
            "source": "system",
            "summary": "Session Started",
        }
    )
    engine.append_event(
        {
            "type": "PromptSubmitted",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=18),
            "source": "claude",
            "actor_tool": "claude",
            "summary": "Prompt Submitted: Generate authentication middleware",
        }
    )
    engine.append_event(
        {
            "type": "ResponseReceived",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=16),
            "source": "claude",
            "actor_tool": "claude",
            "summary": "Response Received: Created JWT middleware",
        }
    )
    engine.append_event(
        {
            "type": "ToolInvocation",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=14),
            "source": "claude",
            "actor_tool": "claude",
            "summary": "Tool Invocation: Read backend/auth.py",
        }
    )
    engine.append_event(
        {
            "type": "filesystem",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=10),
            "source": "filesystem",
            "summary": "Modified backend/auth.py",
        }
    )
    engine.append_event(
        {
            "type": "git",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=5),
            "source": "git",
            "summary": "Commit: feat(authentication)",
        }
    )
    engine.append_event(
        {
            "type": "ErrorOccurred",
            "session_id": "sess-replay-100",
            "timestamp": now - datetime.timedelta(minutes=2),
            "source": "system",
            "summary": "Error Occurred: Connection reset",
        }
    )
    engine.append_event(
        {
            "type": "session",
            "session_id": "sess-replay-100",
            "timestamp": now,
            "source": "system",
            "summary": "Session Ended",
        }
    )

    return engine


def test_replay_engine_resolve_session(populated_session_engine):
    replay_eng = ReplayEngine(populated_session_engine.storage)

    res1 = replay_eng.resolve_session_id("sess-replay-100")
    assert res1 == "sess-replay-100"

    res_latest = replay_eng.resolve_session_id(latest=True)
    assert res_latest == "sess-replay-100"


def test_replay_engine_get_events_and_info(populated_session_engine):
    replay_eng = ReplayEngine(populated_session_engine.storage)
    info = replay_eng.get_session_info("sess-replay-100")

    assert info["session_id"] == "sess-replay-100"
    assert info["total_events"] == 8

    events = replay_eng.get_session_events("sess-replay-100")
    assert len(events) == 8
    assert events[0].summary == "Session Started"
    assert events[-1].summary == "Session Ended"


def test_replay_formatter_json_and_markdown(populated_session_engine):
    replay_eng = ReplayEngine(populated_session_engine.storage)
    info = replay_eng.get_session_info("sess-replay-100")
    events = replay_eng.get_session_events("sess-replay-100")

    json_output = ReplayFormatter.to_json(info, events)
    assert '"session_id": "sess-replay-100"' in json_output
    assert "PromptSubmitted" in json_output

    md_output = ReplayFormatter.to_markdown(info, events)
    assert "# Prometra Session Replay: sess-replay-100" in md_output
    assert "PromptSubmitted" in md_output


def test_replay_exporter(populated_session_engine):
    replay_eng = ReplayEngine(populated_session_engine.storage)
    info = replay_eng.get_session_info("sess-replay-100")
    events = replay_eng.get_session_events("sess-replay-100")

    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "replay.md")
        json_file = os.path.join(tmpdir, "replay.json")

        ReplayExporter.export(info, events, md_file)
        assert os.path.exists(md_file)
        with open(md_file, "r", encoding="utf-8") as f:
            assert "Prometra Session Replay" in f.read()

        ReplayExporter.export(info, events, json_file)
        assert os.path.exists(json_file)
        with open(json_file, "r", encoding="utf-8") as f:
            assert '"session_id"' in f.read()


def test_replay_player_playback(populated_session_engine):
    replay_eng = ReplayEngine(populated_session_engine.storage)
    info = replay_eng.get_session_info("sess-replay-100")
    events = replay_eng.get_session_events("sess-replay-100")

    player = ReplayPlayer()
    # Test instant playback
    player.play(events, info, speed="instant", step=False)
    # Test accelerated playback (10x)
    player.play(events, info, speed="10x", step=False)
    # Test step mode without interactive input prompt
    player.play(events, info, speed="instant", step=True, interactive_input=False)


def test_cli_replay_commands(monkeypatch, populated_session_engine):
    monkeypatch.setattr(
        "prometra.cli.commands.get_storage", lambda: populated_session_engine.storage
    )

    # Test prometra replay --latest
    res_latest = runner.invoke(app, ["replay", "--latest"])
    assert res_latest.exit_code == 0
    assert (
        "sess-replay-100" in res_latest.stdout or "Session Replay" in res_latest.stdout
    )

    # Test prometra replay --session
    res_sess = runner.invoke(app, ["replay", "--session", "sess-replay-100"])
    assert res_sess.exit_code == 0
    assert "sess-replay-100" in res_sess.stdout

    # Test prometra replay --json
    res_json = runner.invoke(app, ["replay", "--latest", "--json"])
    assert res_json.exit_code == 0
    assert '"session_id": "sess-replay-100"' in res_json.stdout

    # Test prometra replay --markdown
    res_md = runner.invoke(app, ["replay", "--latest", "--markdown"])
    assert res_md.exit_code == 0
    assert "# Prometra Session Replay" in res_md.stdout


def test_replay_empty_database(monkeypatch, temp_db):
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: temp_db)
    replay_eng = ReplayEngine(temp_db)
    res = replay_eng.resolve_session_id(latest=True)
    assert res is None

    runner_res = runner.invoke(app, ["replay", "--latest"])
    assert runner_res.exit_code == 0
    assert "No session found to replay" in runner_res.stdout


def test_replay_latest_session_with_empty_newer_session(temp_db):
    engine = TimelineEngine(temp_db)
    now = utcnow()
    db = temp_db.get_session()

    # Session 1: Older session WITH events
    s1 = SessionModel(
        session_id="sess-with-events",
        project_id="test",
        start_ts=now - datetime.timedelta(hours=2),
        end_ts=now - datetime.timedelta(hours=1),
        duration_seconds=3600,
        project_path="/app",
        working_directory="/app",
        status="completed",
    )
    # Session 2: Newer session WITHOUT events
    s2 = SessionModel(
        session_id="sess-empty-newer",
        project_id="test",
        start_ts=now - datetime.timedelta(minutes=10),
        end_ts=now,
        duration_seconds=600,
        project_path="/app",
        working_directory="/app",
        status="completed",
    )
    db.add_all([s1, s2])
    db.commit()
    db.close()

    # Append events for sess-with-events
    engine.append_event(
        {
            "type": "filesystem",
            "session_id": "sess-with-events",
            "timestamp": now - datetime.timedelta(hours=2),
            "source": "filesystem",
            "summary": "File modified: main.py",
        }
    )
    engine.append_event(
        {
            "type": "git",
            "session_id": "sess-with-events",
            "timestamp": now - datetime.timedelta(hours=1),
            "source": "git",
            "summary": "Git Commit: fix bug",
        }
    )

    replay_eng = ReplayEngine(temp_db)
    resolved_id = replay_eng.resolve_session_id(latest=True)

    # Must resolve to the session WITH events, not the empty newer session!
    assert resolved_id == "sess-with-events"
    events = replay_eng.get_session_events(resolved_id)
    assert len(events) == 2
    assert events[0].summary == "File modified: main.py"
    assert events[1].summary == "Git Commit: fix bug"
