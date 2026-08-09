import contextlib
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
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
from prometra.tui.widgets import CommandPaletteModal, HeaderBar, SearchModal, StatusBar


class PrometraTUI(App):
    """Main Textual Interactive Terminal User Interface (TUI) for Prometra."""

    TITLE = "Prometra - Developer Intelligence TUI"
    SUB_TITLE = "Local-First Session Observability"

    CSS = """
    Screen {
        layout: vertical;
        background: #0F172A;
    }
    #main_content {
        height: 1fr;
        padding: 0 1;
    }
    #dialog, #search_dialog {
        padding: 1 2;
        background: #1E293B;
        border: thick $primary;
        width: 60;
        height: auto;
        max-height: 80%;
    }
    #palette_title, #search_modal_title {
        text-style: bold;
        color: #00E5FF;
        margin-bottom: 1;
    }
    #palette_input, #search_modal_input {
        margin-bottom: 1;
    }
    #palette_list {
        height: 10;
        border: solid #334155;
        margin-bottom: 1;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("1", "switch_view('dashboard')", "Dashboard", show=True),
        Binding("2", "switch_view('timeline')", "Timeline", show=True),
        Binding("3", "switch_view('replay')", "Replay", show=True),
        Binding("4", "switch_view('search')", "Search", show=True),
        Binding("5", "switch_view('diff')", "Diff", show=True),
        Binding("6", "switch_view('compare')", "Compare", show=True),
        Binding("7", "switch_view('analytics')", "Analytics", show=True),
        Binding("8", "switch_view('help')", "Help", show=True),
        Binding("9", "switch_view('insights')", "Insights", show=True),
        Binding("0", "switch_view('timemachine')", "TimeMachine", show=True),
        Binding("question_mark", "switch_view('help')", "Help", show=False),
        Binding("ctrl+p", "open_palette", "Command Palette", show=True),
        Binding("ctrl+f", "open_search", "Find", show=True),
        Binding("ctrl+t", "cycle_theme", "Cycle Theme", show=True),
        Binding("r", "refresh_view", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.theme_manager = ThemeManager(default_theme="cyan")
        self.active_view_name: str = "dashboard"

        # Initialize view widgets
        self.view_widgets: dict[str, Static] = {
            "dashboard": DashboardView(storage=self.storage, id="view_dashboard"),
            "timeline": TimelineView(storage=self.storage, id="view_timeline"),
            "replay": ReplayView(storage=self.storage, id="view_replay"),
            "search": SearchView(storage=self.storage, id="view_search"),
            "diff": DiffView(storage=self.storage, id="view_diff"),
            "compare": CompareView(storage=self.storage, id="view_compare"),
            "analytics": AnalyticsView(storage=self.storage, id="view_analytics"),
            "help": HelpView(id="view_help"),
            "insights": InsightsView(storage=self.storage, id="view_insights"),
            "timemachine": TimeMachineView(storage=self.storage, id="view_timemachine"),
        }

    def _get_active_session_id(self) -> str:
        if not self.storage:
            return "No Active Session"
        try:
            db = self.storage.get_session()
            from prometra.storage.models import SessionModel

            active = (
                db.query(SessionModel)
                .filter(SessionModel.status == "active")
                .order_by(SessionModel.start_ts.desc())
                .first()
            )
            if not active:
                active = (
                    db.query(SessionModel)
                    .order_by(SessionModel.start_ts.desc())
                    .first()
                )
            db.close()
            return active.session_id if active else "No Active Session"
        except Exception:  # noqa: BLE001
            return "No Active Session"

    def compose(self) -> ComposeResult:
        yield HeaderBar(
            session_id=self._get_active_session_id(),
            theme_name=self.theme_manager.current_theme_name,
            id="header_bar",
        )
        with Container(id="main_content"):
            yield from self.view_widgets.values()
        yield StatusBar(active_view=self.active_view_name, id="status_bar")

    def on_mount(self) -> None:
        self._update_visible_view()

    def action_switch_view(self, view_name: str) -> None:
        """Switch active view by name ('dashboard', 'timeline', etc.)."""
        if view_name in self.view_widgets:
            self.active_view_name = view_name
            self._update_visible_view()

    def _update_visible_view(self) -> None:
        for name, widget in self.view_widgets.items():
            if name == self.active_view_name:
                widget.display = True
                if hasattr(widget, "refresh_data"):
                    widget.refresh_data()
            else:
                widget.display = False

        with contextlib.suppress(Exception):
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.active_view = self.active_view_name
            status_bar.refresh()

    def action_open_palette(self) -> None:
        def handle_choice(choice: str | None) -> None:
            if not choice or choice in ("cancel", "quit"):
                if choice == "quit":
                    self.exit()
                return

            if choice in ("1", "dash", "dashboard"):
                self.action_switch_view("dashboard")
            elif choice in ("2", "time", "timeline"):
                self.action_switch_view("timeline")
            elif choice in ("3", "repl", "replay"):
                self.action_switch_view("replay")
            elif choice in ("4", "srch", "search"):
                self.action_switch_view("search")
            elif choice in ("5", "diff"):
                self.action_switch_view("diff")
            elif choice in ("6", "comp", "compare"):
                self.action_switch_view("compare")
            elif choice in ("7", "anal", "analytics"):
                self.action_switch_view("analytics")
            elif choice in ("8", "help", "?"):
                self.action_switch_view("help")
            elif choice in ("9", "insights", "intelligence"):
                self.action_switch_view("insights")
            elif choice in ("0", "10", "timemachine", "checkpoint"):
                self.action_switch_view("timemachine")
            elif choice in ("theme", "t"):
                self.action_cycle_theme()
            elif choice in ("refresh", "r"):
                self.action_refresh_view()

        self.push_screen(CommandPaletteModal(), handle_choice)

    def action_open_search(self) -> None:
        def handle_query(query: str | None) -> None:
            if query:
                self.action_switch_view("search")
                search_widget = self.view_widgets["search"]
                if isinstance(search_widget, SearchView):
                    search_widget.perform_search(query)

        self.push_screen(SearchModal(), handle_query)

    def action_cycle_theme(self) -> None:
        new_theme = self.theme_manager.cycle_theme()
        with contextlib.suppress(Exception):
            header = self.query_one("#header_bar", HeaderBar)
            header.theme_name = new_theme
            header.refresh()

    def action_refresh_view(self) -> None:
        active_widget = self.view_widgets.get(self.active_view_name)
        if active_widget and hasattr(active_widget, "refresh_data"):
            active_widget.refresh_data()
