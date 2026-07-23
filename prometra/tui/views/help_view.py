from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static

class HelpView(Static):
    """Interactive Help View rendering keyboard shortcut cheat sheet and documentation reference."""

    def render(self) -> RenderableType:
        key_table = Table("Key Binding", "Action / View Command", "Description", expand=True)

        bindings = [
            ("1", "Switch to Dashboard View", "Overview of metrics, top files, and real-time activity."),
            ("2", "Switch to Timeline View", "Chronological event stream with type filters."),
            ("3", "Switch to Replay View", "Step-by-step coding session playback with speed controls."),
            ("4", "Switch to Search View", "Instant keyword search across SQLite event history."),
            ("5", "Switch to Diff View", "Inspect line-by-line file diffs between sequence checkpoints."),
            ("6", "Switch to Compare View", "Side-by-side session comparison & productivity stats."),
            ("7", "Switch to Analytics View", "Codebase health, AI model token costs, and peak hours."),
            ("8 / ?", "Switch to Help View", "Displays this interactive shortcut cheat sheet."),
            ("Ctrl+P / :", "Open Command Palette", "Quick navigation dialog to jump to any view or action."),
            ("Ctrl+F / /", "Open Search Popup", "Modal search overlay to query event history instantly."),
            ("Ctrl+T", "Toggle Color Theme", "Cycle between Cyan, Dark, Dracula, and High Contrast."),
            ("R", "Refresh View Data", "Re-query SQLite database and update view renderables."),
            ("Space", "Play / Pause Replay", "Toggle session replay animation playback."),
            ("Q / Ctrl+C", "Quit Prometra TUI", "Exit the terminal user interface safely."),
        ]

        for key, cmd, desc in bindings:
            key_table.add_row(f"[bold cyan]{key}[/bold cyan]", cmd, desc)

        info_text = Text()
        info_text.append("🔒 100% Local-First Architecture: ", style="bold green")
        info_text.append("All session metrics, file diffs, and search indexes run locally on your machine via SQLite.\n", style="dim white")

        layout = Table.grid(expand=True)
        layout.add_row(Panel(info_text, title="ℹ️ Local-First Design Guarantees", border_style="green"))
        layout.add_row(Panel(key_table, title="⌨️ Keyboard Navigation Shortcuts", border_style="cyan"))

        return Panel(
            layout,
            title="[8] HELP & SHORTCUT CHEAT SHEET",
            border_style="cyan"
        )
