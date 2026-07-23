import pytest
import os
import json
import tempfile
import datetime
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import SessionModel, TimelineEventModel, FilesystemEventModel, AiEventModel, GitEventModel
from prometra.compare.engine import CompareEngine
from prometra.compare.models import CompareResult, SessionStats
from prometra.compare.formatter import CompareFormatter
from prometra.compare.exporter import CompareExporter
from prometra.core.time import utcnow

runner = CliRunner()

@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_compare.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()

@pytest.fixture
def populated_compare_db(temp_storage):
    db = temp_storage.get_session()

    # Session A (sess-a)
    s_a = SessionModel(
        session_id="sess-a",
        project_id="proj-1",
        start_ts=utcnow() - datetime.timedelta(hours=3),
        duration_seconds=900, # 15 min
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s_a)

    # Session B (sess-b)
    s_b = SessionModel(
        session_id="sess-b",
        project_id="proj-1",
        start_ts=utcnow() - datetime.timedelta(hours=1),
        duration_seconds=1440, # 24 min
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s_b)
    db.commit()

    # Events for Session A (12 filesystem edits, 3 git commits, 7 AI events)
    for i in range(12):
        tl = TimelineEventModel(
            normalized_event_type="filesystem",
            timestamp=utcnow() - datetime.timedelta(hours=3, minutes=15-i),
            sequence=i+1,
            source="filesystem",
            session_id="sess-a",
            summary=f"Modified file_{i}.py"
        )
        db.add(tl)
        fs = FilesystemEventModel(
            event_id=f"fs-a-{i}",
            session_id="sess-a",
            project_id="proj-1",
            timestamp=utcnow() - datetime.timedelta(hours=3, minutes=15-i),
            path=f"file_{i}.py",
            normalized_relative_path=f"file_{i}.py",
            operation="modified",
            source="filesystem"
        )
        db.add(fs)

    for i in range(3):
        tl = TimelineEventModel(
            normalized_event_type="git",
            timestamp=utcnow() - datetime.timedelta(hours=3, minutes=10-i),
            sequence=13+i,
            source="git",
            session_id="sess-a",
            summary=f"Commit #{i}"
        )
        db.add(tl)

    for i in range(7):
        tl = TimelineEventModel(
            normalized_event_type="ai",
            timestamp=utcnow() - datetime.timedelta(hours=3, minutes=5-i),
            sequence=16+i,
            source="claude",
            actor_tool="claude",
            session_id="sess-a",
            summary=f"AI Prompt #{i}"
        )
        db.add(tl)

    # Events for Session B (21 filesystem edits, 6 git commits, 4 AI events)
    for i in range(21):
        tl = TimelineEventModel(
            normalized_event_type="filesystem",
            timestamp=utcnow() - datetime.timedelta(hours=1, minutes=24-i),
            sequence=23+i,
            source="filesystem",
            session_id="sess-b",
            summary=f"Modified file_b_{i}.py"
        )
        db.add(tl)
        fs = FilesystemEventModel(
            event_id=f"fs-b-{i}",
            session_id="sess-b",
            project_id="proj-1",
            timestamp=utcnow() - datetime.timedelta(hours=1, minutes=24-i),
            path=f"file_b_{i}.py",
            normalized_relative_path=f"file_b_{i}.py",
            operation="modified",
            source="filesystem"
        )
        db.add(fs)

    for i in range(6):
        tl = TimelineEventModel(
            normalized_event_type="git",
            timestamp=utcnow() - datetime.timedelta(hours=1, minutes=10-i),
            sequence=44+i,
            source="git",
            session_id="sess-b",
            summary=f"Commit B #{i}"
        )
        db.add(tl)

    for i in range(4):
        tl = TimelineEventModel(
            normalized_event_type="ai",
            timestamp=utcnow() - datetime.timedelta(hours=1, minutes=4-i),
            sequence=50+i,
            source="claude",
            actor_tool="claude",
            session_id="sess-b",
            summary=f"AI Prompt B #{i}"
        )
        db.add(tl)

    db.commit()
    db.close()
    return temp_storage

def test_basic_comparison(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")

    assert res.session_a == "sess-a"
    assert res.session_b == "sess-b"
    assert res.stats_a.duration_minutes == 15
    assert res.stats_b.duration_minutes == 24
    assert res.stats_a.files_modified == 12
    assert res.stats_b.files_modified == 21
    assert res.stats_a.git_commits == 3
    assert res.stats_b.git_commits == 6
    assert res.stats_a.ai_events == 7
    assert res.stats_b.ai_events == 4

    assert res.duration_difference == "+9 min"
    assert res.files_modified_difference == 9
    assert res.git_commit_difference == 3
    assert res.ai_event_difference == -3

def test_same_session(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    with pytest.raises(ValueError) as excinfo:
        engine.compare_sessions("sess-a", "sess-a")
    assert "Cannot compare session 'sess-a' with itself" in str(excinfo.value)

def test_missing_session(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    with pytest.raises(ValueError) as excinfo:
        engine.compare_sessions("sess-a", "nonexistent_session_id")
    assert "Session 'nonexistent_session_id' not found" in str(excinfo.value)

def test_latest_comparison(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    # sess-b is most recent, sess-a is 2nd most recent
    res = engine.compare_sessions(latest=True)
    assert res.session_a == "sess-a"
    assert res.session_b == "sess-b"

def test_latest_not_enough_sessions(temp_storage):
    engine = CompareEngine(temp_storage)
    with pytest.raises(ValueError) as excinfo:
        engine.compare_sessions(latest=True)
    assert "At least two sessions are required" in str(excinfo.value)

def test_json_output(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")
    json_str = CompareExporter.to_json(res)
    data = json.loads(json_str)

    assert data["session_a"] == "sess-a"
    assert data["session_b"] == "sess-b"
    assert data["duration_difference"] == "+9 min"
    assert data["files_modified_difference"] == 9
    assert data["git_commit_difference"] == 3
    assert data["ai_event_difference"] == -3
    assert "timeline_difference" in data

def test_markdown_output(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")
    md = CompareExporter.to_markdown(res)

    assert "# Session Comparison" in md
    assert "## Summary Table" in md
    assert "## Timeline Comparison" in md
    assert "## Statistics & Productivity" in md

def test_export_option(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "compare.json")
        CompareExporter.export_to_file(res, json_path)
        assert os.path.exists(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert '"session_a": "sess-a"' in content

        md_path = os.path.join(tmpdir, "compare.md")
        CompareExporter.export_to_file(res, md_path)
        assert os.path.exists(md_path)
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "# Session Comparison" in content

def test_statistics_and_productivity(populated_compare_db):
    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")

    assert res.stats_a.productivity_metrics["events_per_minute"] > 0
    assert res.stats_b.productivity_metrics["events_per_minute"] > 0
    assert "files_changed_per_minute" in res.stats_a.productivity_metrics
    assert "commits_per_hour" in res.stats_a.productivity_metrics

def test_cli_compare_command(monkeypatch, populated_compare_db):
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: populated_compare_db)

    res_help = runner.invoke(app, ["compare", "--help"])
    assert res_help.exit_code == 0
    assert "Compare metrics and activity between two development sessions" in res_help.stdout

    res_latest = runner.invoke(app, ["compare", "--latest"])
    assert res_latest.exit_code == 0
    assert "Session Comparison" in res_latest.stdout

    res_json = runner.invoke(app, ["compare", "sess-a", "sess-b", "--json"])
    assert res_json.exit_code == 0
    assert '"session_a": "sess-a"' in res_json.stdout

    res_md = runner.invoke(app, ["compare", "sess-a", "sess-b", "--markdown"])
    assert res_md.exit_code == 0
    assert "# Session Comparison" in res_md.stdout

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "report.json")
        res_exp = runner.invoke(app, ["compare", "sess-a", "sess-b", "--json", "--export", out_file])
        assert res_exp.exit_code == 0
        assert os.path.exists(out_file)

def test_compare_renderer(populated_compare_db):
    from prometra.compare.renderer import CompareRenderer
    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")
    renderer = CompareRenderer()
    renderer.render(res)

def test_compare_options_and_formatter_dict(populated_compare_db):
    from prometra.compare.models import CompareOptions
    from prometra.compare.formatter import CompareFormatter
    opts = CompareOptions(session_a="sess-a", session_b="sess-b", latest=True)
    assert opts.session_a == "sess-a"
    assert opts.latest is True

    engine = CompareEngine(populated_compare_db)
    res = engine.compare_sessions("sess-a", "sess-b")
    d = CompareFormatter.to_dict(res)
    assert d["session_a"] == "sess-a"
    assert d["session_b"] == "sess-b"

