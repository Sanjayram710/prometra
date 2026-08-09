import datetime
import os
import tempfile

import pytest
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.core.time import utcnow
from prometra.storage.models import (
    AiEventModel,
    FilesystemEventModel,
    SessionModel,
    TimelineEventModel,
    WorkspaceModel,
)
from prometra.storage.sqlite import SQLiteStorage
from prometra.tui.app import PrometraTUI
from prometra.tui.theme import ThemeManager
from prometra.tui.views import (
    AnalyticsView,
    CompareView,
    DashboardView,
    DiffView,
    HelpView,
    InsightsView,
    ReplayView,
    SearchView,
    TimelineView,
    TimeMachineView,
)
from prometra.tui.widgets import (
    HeaderBar,
    MetricCard,
    StatusBar,
)

runner = CliRunner()


@pytest.fixture
def populated_tui_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_tui_real.db")
        storage = SQLiteStorage(db_path)
        db = storage.get_session()

        ws = WorkspaceModel(
            project_id="tui_proj",
            name="tui_proj",
            root_path=tmpdir,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(ws)

        s1 = SessionModel(
            session_id="sess-tui-1",
            project_id="tui_proj",
            start_ts=utcnow() - datetime.timedelta(hours=1),
            duration_seconds=1800,
            project_path=tmpdir,
            working_directory=tmpdir,
            status="active",
        )
        db.add(s1)

        tl1 = TimelineEventModel(
            normalized_event_type="filesystem",
            timestamp=utcnow() - datetime.timedelta(minutes=40),
            sequence=1,
            source="filesystem",
            session_id="sess-tui-1",
            summary="File modified: hello.py",
        )
        tl2 = TimelineEventModel(
            normalized_event_type="ai_prompt",
            timestamp=utcnow() - datetime.timedelta(minutes=20),
            sequence=2,
            source="claude",
            session_id="sess-tui-1",
            summary="Prompt: Add hello function",
        )
        db.add_all([tl1, tl2])

        fs1 = FilesystemEventModel(
            event_id="fs-tui-1",
            session_id="sess-tui-1",
            project_id="tui_proj",
            timestamp=utcnow() - datetime.timedelta(minutes=40),
            operation="modified",
            path="hello.py",
            normalized_relative_path="hello.py",
        )
        db.add(fs1)

        ai1 = AiEventModel(
            event_id="ai-tui-1",
            session_id="sess-tui-1",
            timestamp=utcnow() - datetime.timedelta(minutes=20),
            event_type="UserPrompt",
            connector="claude",
            description="Prompt: Add hello function",
        )
        db.add(ai1)

        db.commit()
        db.close()

        try:
            yield storage
        finally:
            storage.engine.dispose()


def test_theme_manager():
    tm = ThemeManager(default_theme="cyan")
    assert tm.current_theme_name == "cyan"
    assert "primary" in tm.current_theme

    next_theme = tm.cycle_theme()
    assert next_theme == "dark"

    assert tm.set_theme("dracula") is True
    assert tm.current_theme_name == "dracula"

    assert tm.set_theme("nonexistent") is False


def test_metric_card():
    card = MetricCard(
        "Total Events", "1,234", subtitle="Recent edits", icon="⚡", color="cyan"
    )
    rendered = card.render()
    assert rendered is not None


def test_header_and_status_bar():
    header = HeaderBar(session_id="sess-tui-1", theme_name="cyan")
    hdr_rendered = header.render()
    assert hdr_rendered is not None

    status = StatusBar(active_view="timeline")
    st_rendered = status.render()
    assert st_rendered is not None


def test_dashboard_view(populated_tui_storage):
    view = DashboardView(storage=populated_tui_storage)
    view.refresh_data()
    assert view.metrics_data["total_sessions"] == 1
    assert view.metrics_data["active_session"] == "sess-tui-1"
    assert len(view.recent_events) >= 1
    rendered = view.render()
    assert rendered is not None


def test_timeline_view(populated_tui_storage):
    view = TimelineView(storage=populated_tui_storage)
    view.refresh_data()
    assert len(view.events_data) == 2
    rendered = view.render()
    assert rendered is not None


def test_replay_view(populated_tui_storage):
    view = ReplayView(storage=populated_tui_storage)
    view.refresh_data()
    assert len(view.events_list) == 2
    view.toggle_play()
    assert view.is_playing is True

    view.step_forward()
    assert view.current_step == 2

    view.step_backward()
    assert view.current_step == 1

    rendered = view.render()
    assert rendered is not None


def test_search_view(populated_tui_storage):
    view = SearchView(storage=populated_tui_storage)
    view.perform_search("hello")
    assert len(view.search_results) >= 1
    rendered = view.render()
    assert rendered is not None


def test_diff_view(populated_tui_storage):
    view = DiffView(storage=populated_tui_storage)
    view.load_diff("hello.py")
    assert view.file_path == "hello.py"
    rendered = view.render()
    assert rendered is not None


def test_compare_view(populated_tui_storage):
    view = CompareView(storage=populated_tui_storage)
    view.load_comparison("sess-tui-1", "sess-tui-1")
    rendered = view.render()
    assert rendered is not None


def test_analytics_view(populated_tui_storage):
    view = AnalyticsView(storage=populated_tui_storage)
    view.refresh_data()
    assert view.analytics_data["total_tokens"] > 0
    rendered = view.render()
    assert rendered is not None


def test_insights_view(populated_tui_storage):
    view = InsightsView(storage=populated_tui_storage)
    view.refresh_data()
    assert view.insights_data is not None
    rendered = view.render()
    assert rendered is not None


def test_timemachine_view(populated_tui_storage):
    view = TimeMachineView(storage=populated_tui_storage)
    view.refresh_data()
    rendered = view.render()
    assert rendered is not None


def test_help_view():
    view = HelpView()
    rendered = view.render()
    assert rendered is not None


def test_tui_app_instantiation(populated_tui_storage):
    tui = PrometraTUI(storage=populated_tui_storage)
    assert tui.TITLE == "Prometra - Developer Intelligence TUI"

    tui.action_switch_view("timeline")
    assert tui.active_view_name == "timeline"

    tui.action_cycle_theme()
    assert tui.theme_manager.current_theme_name == "dark"

    tui.action_refresh_view()


def test_cli_ui_help():
    res = runner.invoke(app, ["ui", "--help"])
    assert res.exit_code == 0
    assert (
        "interactive terminal user interface" in res.stdout.lower()
        or "tui" in res.stdout.lower()
    )
