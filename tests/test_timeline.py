import pytest
import os
import tempfile
import datetime
from typer.testing import CliRunner
from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, SessionModel
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter
from prometra.timeline.formatter import TimelineFormatter
from prometra.timeline.renderer import TimelineRenderer
from prometra.core.time import utcnow

runner = CliRunner()

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_prometra.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()

@pytest.fixture
def populated_engine(temp_db):
    engine = TimelineEngine(temp_db)
    
    # Session 1 events
    engine.append_event({
        "type": "filesystem",
        "session_id": "sess-1",
        "timestamp": utcnow() - datetime.timedelta(hours=2),
        "path": "src/main.py",
        "normalized_relative_path": "src/main.py",
        "operation": "modified",
        "summary": "Modified src/main.py for authentication logic"
    })
    engine.append_event({
        "type": "git",
        "session_id": "sess-1",
        "timestamp": utcnow() - datetime.timedelta(hours=1),
        "repository": "prometra",
        "branch": "main",
        "commit_id": "abc1234",
        "message": "feat: add authentication layer",
        "summary": "Commit: feat: add authentication layer"
    })
    engine.append_event({
        "type": "ai",
        "session_id": "sess-1",
        "timestamp": utcnow() - datetime.timedelta(minutes=30),
        "actor_tool": "claude",
        "source": "claude",
        "summary": "AI Prompt: Implement JWT authentication function"
    })
    
    # Session 2 events
    engine.append_event({
        "type": "filesystem",
        "session_id": "sess-2",
        "timestamp": utcnow() - datetime.timedelta(days=2),
        "path": "docs/readme.md",
        "normalized_relative_path": "docs/readme.md",
        "operation": "created",
        "summary": "Created docs/readme.md"
    })
    engine.append_event({
        "type": "connector",
        "session_id": "sess-2",
        "timestamp": utcnow() - datetime.timedelta(days=2),
        "actor_tool": "claude",
        "source": "claude",
        "summary": "Connector Claude initialized"
    })
    
    # Register session models
    db = temp_db.get_session()
    s1 = SessionModel(
        session_id="sess-1",
        project_id="test_project",
        start_ts=utcnow() - datetime.timedelta(hours=3),
        end_ts=utcnow() - datetime.timedelta(minutes=10),
        duration_seconds=10400,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    s2 = SessionModel(
        session_id="sess-2",
        project_id="test_project",
        start_ts=utcnow() - datetime.timedelta(days=2, hours=1),
        end_ts=utcnow() - datetime.timedelta(days=2),
        duration_seconds=3600,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s1)
    db.add(s2)
    db.commit()
    db.close()
    
    return engine

def test_timeline_empty_db(temp_db):
    engine = TimelineEngine(temp_db)
    events = engine.get_events()
    assert len(events) == 0
    
    summary = engine.get_summary(TimelineFilter())
    assert summary.total_events == 0
    assert summary.sessions_count == 0

def test_timeline_filter_session(populated_engine):
    events = populated_engine.get_events(session_id="sess-1")
    assert len(events) == 3
    for e in events:
        assert e.session_id == "sess-1"

def test_timeline_filter_type(populated_engine):
    fs_events = populated_engine.get_events(event_type="filesystem")
    assert len(fs_events) == 2
    for e in fs_events:
        assert e.normalized_event_type == "filesystem"

    git_events = populated_engine.get_events(event_type="git")
    assert len(git_events) == 1
    assert git_events[0].normalized_event_type == "git"

    ai_events = populated_engine.get_events(event_type="ai")
    assert len(ai_events) >= 1

def test_timeline_filter_connector(populated_engine):
    claude_events = populated_engine.get_events(connector="claude")
    assert len(claude_events) == 2

def test_timeline_filter_search(populated_engine):
    auth_events = populated_engine.get_events(search="authentication")
    assert len(auth_events) == 3
    
    jwt_events = populated_engine.get_events(search="JWT")
    assert len(jwt_events) == 1

def test_timeline_filter_today(populated_engine):
    today_events = populated_engine.get_events(today=True)
    assert len(today_events) == 3

def test_timeline_limit_and_reverse(populated_engine):
    limited = populated_engine.get_events(limit=2)
    assert len(limited) == 2
    
    normal_order = populated_engine.get_events()
    reversed_order = populated_engine.get_events(reverse=True)
    assert normal_order[0].id == reversed_order[-1].id
    assert normal_order[-1].id == reversed_order[0].id

def test_timeline_summary(populated_engine):
    summary = populated_engine.get_summary(TimelineFilter())
    assert summary.total_events == 5
    assert summary.sessions_count == 2
    assert summary.files_modified == 2
    assert summary.git_commits == 1
    assert summary.ai_events == 2
    assert "claude" in summary.connectors_used

def test_timeline_grouped(populated_engine):
    grouped = populated_engine.get_grouped(TimelineFilter())
    assert len(grouped) == 2
    
    sess1_group = next(g for g in grouped if g["session_id"] == "sess-1")
    assert sess1_group["files_changed"] == 1
    assert sess1_group["git_commits"] == 1
    assert sess1_group["ai_events"] == 1
    assert len(sess1_group["events"]) == 3

def test_timeline_export(populated_engine):
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "timeline.md")
        csv_file = os.path.join(tmpdir, "timeline.csv")
        json_file = os.path.join(tmpdir, "timeline.json")
        
        populated_engine.export_events(TimelineFilter(), md_file)
        assert os.path.exists(md_file)
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "| Timestamp | Category |" in content
            
        populated_engine.export_events(TimelineFilter(), csv_file)
        assert os.path.exists(csv_file)
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Timestamp,Category,Source" in content
            
        populated_engine.export_events(TimelineFilter(), json_file)
        assert os.path.exists(json_file)
        with open(json_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert '"session_id": "sess-1"' in content

def test_timeline_large_database(temp_db):
    """Simulate large database performance with 1,000 events."""
    engine = TimelineEngine(temp_db)
    now = utcnow()
    
    # Bulk insert
    db = temp_db.get_session()
    events = []
    for i in range(1000):
        events.append(TimelineEventModel(
            normalized_event_type="filesystem" if i % 2 == 0 else "git",
            timestamp=now - datetime.timedelta(seconds=i),
            sequence=i + 1,
            source="test",
            session_id=f"sess-{i % 10}",
            summary=f"Event number {i} description"
        ))
    db.bulk_save_objects(events)
    db.commit()
    db.close()
    
    # Test query with limit & pagination
    page1 = engine.get_events(limit=50, offset=0)
    assert len(page1) == 50
    assert page1[0].sequence == 1
    
    page2 = engine.get_events(limit=50, offset=50)
    assert len(page2) == 50
    assert page2[0].sequence == 51
    
    search_res = engine.get_events(search="number 99")
    assert len(search_res) >= 1

def test_cli_timeline_flags(monkeypatch, populated_engine):
    # Test timeline CLI invocation with various options
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: populated_engine.storage)
    
    res = runner.invoke(app, ["timeline", "--summary"])
    assert res.exit_code == 0
    assert "Timeline Summary" in res.stdout
    
    res = runner.invoke(app, ["timeline", "--type", "git"])
    assert res.exit_code == 0
    
    res = runner.invoke(app, ["timeline", "--search", "authentication"])
    assert res.exit_code == 0
    
    res = runner.invoke(app, ["timeline", "--group", "session"])
    assert res.exit_code == 0
    assert "Session #sess-1" in res.stdout
    
    res = runner.invoke(app, ["timeline", "--json"])
    assert res.exit_code == 0
    assert "normalized_event_type" in res.stdout
