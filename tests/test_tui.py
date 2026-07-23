import pytest
import os
import tempfile
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.tui.theme import ThemeManager, THEMES
from prometra.tui.widgets import MetricCard, HeaderBar, StatusBar, CommandPaletteModal, SearchModal
from prometra.tui.views import (
    DashboardView,
    TimelineView,
    ReplayView,
    SearchView,
    DiffView,
    CompareView,
    AnalyticsView,
    HelpView,
)
from prometra.tui.app import PrometraTUI
from prometra.storage.sqlite import SQLiteStorage

runner = CliRunner()

@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_tui.db")
        storage = SQLiteStorage(db_path)
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
    card = MetricCard("Total Events", "1,234", subtitle="Recent edits", icon="⚡", color="cyan")
    rendered = card.render()
    assert rendered is not None

def test_header_and_status_bar():
    header = HeaderBar(session_id="sess-123", theme_name="cyan")
    hdr_rendered = header.render()
    assert hdr_rendered is not None

    status = StatusBar(active_view="timeline")
    st_rendered = status.render()
    assert st_rendered is not None

def test_dashboard_view(temp_storage):
    view = DashboardView(storage=temp_storage)
    view.refresh_data()
    rendered = view.render()
    assert rendered is not None

def test_timeline_view(temp_storage):
    view = TimelineView(storage=temp_storage)
    view.refresh_data()
    rendered = view.render()
    assert rendered is not None

def test_replay_view(temp_storage):
    view = ReplayView(storage=temp_storage)
    view.refresh_data()
    view.toggle_play()
    assert view.is_playing is True

    view.step_forward()
    assert view.current_step == 2

    view.step_backward()
    assert view.current_step == 1

    rendered = view.render()
    assert rendered is not None

def test_search_view(temp_storage):
    view = SearchView(storage=temp_storage)
    view.perform_search("hello")
    assert len(view.search_results) > 0
    rendered = view.render()
    assert rendered is not None

def test_diff_view(temp_storage):
    view = DiffView(storage=temp_storage)
    view.load_diff("hello.py")
    assert view.file_path == "hello.py"
    rendered = view.render()
    assert rendered is not None

def test_compare_view(temp_storage):
    view = CompareView(storage=temp_storage)
    view.load_comparison("sess-a", "sess-b")
    rendered = view.render()
    assert rendered is not None

def test_analytics_view(temp_storage):
    view = AnalyticsView(storage=temp_storage)
    view.refresh_data()
    rendered = view.render()
    assert rendered is not None

def test_help_view():
    view = HelpView()
    rendered = view.render()
    assert rendered is not None

def test_tui_app_instantiation(temp_storage):
    tui = PrometraTUI(storage=temp_storage)
    assert tui.TITLE == "Prometra - Developer Intelligence TUI"

    tui.action_switch_view("timeline")
    assert tui.active_view_name == "timeline"

    tui.action_cycle_theme()
    assert tui.theme_manager.current_theme_name == "dark"

    tui.action_refresh_view()

def test_cli_ui_help():
    res = runner.invoke(app, ["ui", "--help"])
    assert res.exit_code == 0
    assert "interactive terminal user interface" in res.stdout.lower() or "tui" in res.stdout.lower()
