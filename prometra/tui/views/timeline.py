from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter


class TimelineView(Static):
    """Interactive Timeline View displaying live event history table loaded from SQLite DB."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.events_data: list[dict[str, Any]] = []

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if self.storage:
            try:
                engine = TimelineEngine(self.storage)
                query_res = engine.query_events(filters=TimelineFilter(limit=30))
                self.events_data = [
                    {
                        "id": e.id,
                        "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if e.timestamp
                        else "N/A",
                        "type": e.normalized_event_type,
                        "source": e.source,
                        "summary": e.summary or "Event logged",
                        "session": e.session_id or "default",
                    }
                    for e in query_res
                ]
            except Exception:  # noqa: BLE001
                self.events_data = []
        else:
            self.events_data = []

        self.refresh()

    def render(self) -> RenderableType:
        table = Table(
            "ID",
            "Timestamp",
            "Category",
            "Source",
            "Summary",
            "Session ID",
            expand=True,
        )

        type_colors = {
            "filesystem": "green",
            "ai_prompt": "magenta",
            "ai_tool": "bright_magenta",
            "git_commit": "yellow",
            "session": "cyan",
        }

        if self.events_data:
            for ev in self.events_data:
                c = type_colors.get(ev["type"], "white")
                table.add_row(
                    str(ev["id"]),
                    ev["timestamp"],
                    f"[{c}]{ev['type']}[/{c}]",
                    ev["source"],
                    ev["summary"],
                    ev["session"],
                )
        else:
            table.add_row(
                "-",
                "-",
                "[dim]No events[/dim]",
                "-",
                "[dim]No events recorded in project history.[/dim]",
                "-",
            )

        return Panel(
            table, title="[2] INTERACTIVE EVENT TIMELINE", border_style="yellow"
        )
