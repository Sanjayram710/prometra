from typing import Optional, List, Dict, Any, Callable
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static, Input, Button, Label, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.screen import ModalScreen
from textual.app import RenderResult

class MetricCard(Static):
    """Reusable metric card component displaying title, bold value, icon, and status."""

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        icon: str = "📊",
        color: str = "cyan",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.card_title = title
        self.card_value = value
        self.card_subtitle = subtitle
        self.card_icon = icon
        self.card_color = color

    def render(self) -> RenderableType:
        content = Text()
        content.append(f"{self.card_icon} {self.card_title.upper()}\n", style=f"bold {self.card_color}")
        content.append(f"{self.card_value}\n", style="bold white")
        if self.card_subtitle:
            content.append(f"{self.card_subtitle}", style="dim gray")

        return Panel(
            content,
            border_style=self.card_color,
            padding=(0, 1)
        )

class HeaderBar(Static):
    """Custom Header widget displaying Prometra title, active session, and clock."""

    def __init__(self, session_id: str = "No Active Session", theme_name: str = "cyan", **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.theme_name = theme_name

    def render(self) -> RenderableType:
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="center", ratio=2)
        table.add_column(justify="right", ratio=1)

        left_text = Text("🚀 PROMETRA TUI", style="bold cyan")
        center_text = Text(f"Session: {self.session_id}", style="bold yellow")
        right_text = Text(f"Theme: {self.theme_name.upper()} | Local-First", style="dim white")

        table.add_row(left_text, center_text, right_text)
        return Panel(table, style="on #1E293B", border_style="cyan")

class StatusBar(Static):
    """Footer status bar widget displaying view shortcuts and status indicators."""

    def __init__(self, active_view: str = "Dashboard", **kwargs):
        super().__init__(**kwargs)
        self.active_view = active_view

    def render(self) -> RenderableType:
        shortcuts = " [1]Dash [2]Time [3]Repl [4]Srch [5]Diff [6]Comp [7]Anal [8]Help [9]Insights [0]TimeMachine | [Ctrl+P]Cmd | [Ctrl+F]Find | [Ctrl+T]Theme | [Q]Quit"
        status_text = Text()
        status_text.append(f" VIEW: {self.active_view.upper()} |", style="bold green")
        status_text.append(shortcuts, style="dim white")
        return Panel(status_text, style="on #0F172A", border_style="blue", padding=(0, 0))

class CommandPaletteModal(ModalScreen[str]):
    """Modal screen for Command Palette (Ctrl+P)."""

    COMMANDS = [
        ("1", "Dashboard - Overview Metrics & Activity"),
        ("2", "Timeline - Interactive Event Stream"),
        ("3", "Replay - Coding Session Player"),
        ("4", "Search - Instant Event Query Engine"),
        ("5", "Diff - File Version Diff Viewer"),
        ("6", "Compare - Session Comparison Engine"),
        ("7", "Analytics - Codebase Health & Token Usage"),
        ("8", "Help - Keyboard Shortcuts & Documentation"),
        ("9", "Insights - AI Session Intelligence & Recommendations"),
        ("0", "Time Machine - Checkpoint Browser & State Restore"),
        ("T", "Toggle Theme (Cyan / Dark / Dracula / Contrast)"),
        ("R", "Refresh Data"),
        ("Q", "Quit Prometra TUI"),
    ]

    def compose(self):
        with Vertical(id="dialog"):
            yield Label("⚡ COMMAND PALETTE", id="palette_title")
            yield Input(placeholder="Type view number (0-9), action, or filter...", id="palette_input")
            with ListView(id="palette_list"):
                for key, label in self.COMMANDS:
                    yield ListItem(Label(f"[{key}] {label}"))
            yield Button("Close (Esc)", id="close_palette_btn")

    def on_input_submitted(self, event: Input.Submitted):
        val = event.value.strip().lower()
        if val in ("1", "dash", "dashboard"):
            self.dismiss("1")
        elif val in ("2", "time", "timeline"):
            self.dismiss("2")
        elif val in ("3", "repl", "replay"):
            self.dismiss("3")
        elif val in ("4", "srch", "search"):
            self.dismiss("4")
        elif val in ("5", "diff"):
            self.dismiss("5")
        elif val in ("6", "comp", "compare"):
            self.dismiss("6")
        elif val in ("7", "anal", "analytics"):
            self.dismiss("7")
        elif val in ("8", "help", "?"):
            self.dismiss("8")
        elif val in ("9", "insights", "intelligence"):
            self.dismiss("9")
        elif val in ("0", "10", "timemachine", "checkpoint"):
            self.dismiss("0")
        elif val in ("t", "theme"):
            self.dismiss("theme")
        elif val in ("r", "refresh"):
            self.dismiss("refresh")
        elif val in ("q", "quit"):
            self.dismiss("quit")
        else:
            self.dismiss(val)

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss("cancel")

class SearchModal(ModalScreen[str]):
    """Modal screen for Search Popup (Ctrl+F)."""

    def compose(self):
        with Vertical(id="search_dialog"):
            yield Label("🔍 SEARCH EVENT HISTORY", id="search_modal_title")
            yield Input(placeholder="Enter search keyword (e.g. auth, git, file.py)...", id="search_modal_input")
            yield Button("Search", id="search_modal_btn")

    def on_input_submitted(self, event: Input.Submitted):
        self.dismiss(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed):
        inp = self.query_one("#search_modal_input", Input)
        self.dismiss(inp.value.strip())
