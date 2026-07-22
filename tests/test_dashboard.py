import pytest
import os
import tempfile
import datetime
from typer.testing import CliRunner
from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, SessionModel, FilesystemEventModel, GitEventModel, AiEventModel
from prometra.timeline.engine import TimelineEngine
from prometra.dashboard.engine import DashboardEngine
from prometra.dashboard.formatter import DashboardFormatter
from prometra.dashboard.exporter import DashboardExporter
from prometra.core.time import utcnow

runner = CliRunner()

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_dashboard.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()

@pytest.fixture
def populated_dashboard_db(temp_db):
    now = utcnow()
    db = temp_db.get_session()

    # Create Session 1 (Today)
    s1 = SessionModel(
        session_id="sess-dash-1",
        project_id="test_project",
        start_ts=now - datetime.timedelta(hours=2),
        end_ts=now,
        duration_seconds=7200,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    # Create Session 2 (5 days ago)
    s2 = SessionModel(
        session_id="sess-dash-2",
        project_id="test_project",
        start_ts=now - datetime.timedelta(days=5),
        end_ts=now - datetime.timedelta(days=5) + datetime.timedelta(hours=1),
        duration_seconds=3600,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s1)
    db.add(s2)

    # Filesystem Events
    f1 = FilesystemEventModel(
        event_id="fs-1",
        session_id="sess-dash-1",
        project_id="test_project",
        timestamp=now - datetime.timedelta(hours=1),
        path="backend/auth.py",
        normalized_relative_path="backend/auth.py",
        operation="modified",
        source="filesystem"
    )
    f2 = FilesystemEventModel(
        event_id="fs-2",
        session_id="sess-dash-1",
        project_id="test_project",
        timestamp=now - datetime.timedelta(hours=1),
        path="backend/auth.py",
        normalized_relative_path="backend/auth.py",
        operation="modified",
        source="filesystem"
    )
    f3 = FilesystemEventModel(
        event_id="fs-3",
        session_id="sess-dash-2",
        project_id="test_project",
        timestamp=now - datetime.timedelta(days=5),
        path="frontend/login.tsx",
        normalized_relative_path="frontend/login.tsx",
        operation="created",
        source="filesystem"
    )
    db.add_all([f1, f2, f3])

    # Git Events
    g1 = GitEventModel(
        event_id="git-1",
        repository="prometra",
        branch="main",
        commit_id="c111",
        timestamp=now - datetime.timedelta(hours=1),
        source="git"
    )
    db.add(g1)

    # AI Events
    ai1 = AiEventModel(
        event_id="ai-1",
        session_id="sess-dash-1",
        timestamp=now - datetime.timedelta(hours=1),
        event_type="PromptSubmitted",
        connector="claude",
        model_name="claude-3-5-sonnet",
        prompt_id="p1",
        token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        cost=0.005,
        description="Prompt Submitted: auth"
    )
    ai2 = AiEventModel(
        event_id="ai-2",
        session_id="sess-dash-1",
        timestamp=now - datetime.timedelta(hours=1),
        event_type="ResponseReceived",
        connector="claude",
        model_name="claude-3-5-sonnet",
        token_usage={"prompt_tokens": 200, "completion_tokens": 300, "total_tokens": 500},
        cost=0.010,
        description="Response Received"
    )
    db.add_all([ai1, ai2])

    # Timeline Events
    tl1 = TimelineEventModel(
        normalized_event_type="PromptSubmitted",
        timestamp=now - datetime.timedelta(hours=1),
        sequence=1,
        source="claude",
        actor_tool="claude",
        session_id="sess-dash-1",
        summary="Prompt Submitted"
    )
    db.add(tl1)

    db.commit()
    db.close()

    return temp_db

def test_dashboard_engine_all_time(populated_dashboard_db):
    engine = DashboardEngine(populated_dashboard_db)
    metrics = engine.compute_metrics()

    assert metrics.sessions.total_sessions == 2
    assert metrics.sessions.total_duration_seconds == 10800
    assert metrics.sessions.longest_session_seconds == 7200

    assert metrics.filesystem.files_modified == 2
    assert metrics.filesystem.files_created == 1

    assert len(metrics.filesystem.top_edited_files) >= 1
    assert metrics.filesystem.top_edited_files[0].path == "backend/auth.py"
    assert metrics.filesystem.top_edited_files[0].edits == 2

    assert metrics.ai.ai_prompts == 1
    assert metrics.ai.ai_responses == 1
    assert metrics.ai.total_tokens == 650
    assert metrics.ai.estimated_cost == 0.015
    assert metrics.ai.top_models[0].model_name == "claude-3-5-sonnet"

def test_dashboard_engine_today_filter(populated_dashboard_db):
    engine = DashboardEngine(populated_dashboard_db)
    metrics_today = engine.compute_metrics(today=True)

    assert metrics_today.filter_label == "Today"
    assert metrics_today.sessions.total_sessions == 1
    assert metrics_today.filesystem.files_created == 0 # created file was 5 days ago

def test_dashboard_engine_week_filter(populated_dashboard_db):
    engine = DashboardEngine(populated_dashboard_db)
    metrics_week = engine.compute_metrics(week=True)

    assert metrics_week.filter_label == "Past 7 Days"
    assert metrics_week.sessions.total_sessions == 2

def test_dashboard_engine_session_filter(populated_dashboard_db):
    engine = DashboardEngine(populated_dashboard_db)
    metrics_sess = engine.compute_metrics(session_id="sess-dash-1")

    assert metrics_sess.filter_label == "Session #sess-dash-1"
    assert metrics_sess.sessions.total_sessions == 1
    assert metrics_sess.sessions.total_duration_seconds == 7200

def test_dashboard_formatter(populated_dashboard_db):
    engine = DashboardEngine(populated_dashboard_db)
    metrics = engine.compute_metrics()

    json_out = DashboardFormatter.to_json(metrics)
    assert '"total_sessions": 2' in json_out
    assert "claude-3-5-sonnet" in json_out

    md_out = DashboardFormatter.to_markdown(metrics)
    assert "# Prometra Analytics Dashboard" in md_out
    assert "backend/auth.py" in md_out
    assert "claude-3-5-sonnet" in md_out

def test_dashboard_exporter(populated_dashboard_db):
    engine = DashboardEngine(populated_dashboard_db)
    metrics = engine.compute_metrics()

    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "dashboard.md")
        json_file = os.path.join(tmpdir, "dashboard.json")

        DashboardExporter.export(metrics, md_file)
        assert os.path.exists(md_file)
        with open(md_file, "r", encoding="utf-8") as f:
            assert "Prometra Analytics Dashboard" in f.read()

        DashboardExporter.export(metrics, json_file)
        assert os.path.exists(json_file)
        with open(json_file, "r", encoding="utf-8") as f:
            assert '"filter_label"' in f.read()

def test_cli_dashboard_command(monkeypatch, populated_dashboard_db):
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: populated_dashboard_db)

    res = runner.invoke(app, ["dashboard"])
    assert res.exit_code == 0
    assert "Prometra Analytics Dashboard" in res.stdout

    res_today = runner.invoke(app, ["dashboard", "--today"])
    assert res_today.exit_code == 0
    assert "Today" in res_today.stdout

    res_json = runner.invoke(app, ["dashboard", "--json"])
    assert res_json.exit_code == 0
    assert '"filter_label"' in res_json.stdout

    res_md = runner.invoke(app, ["dashboard", "--markdown"])
    assert res_md.exit_code == 0
    assert "# Prometra Analytics Dashboard" in res_md.stdout
