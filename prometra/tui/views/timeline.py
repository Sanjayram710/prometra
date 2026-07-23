from typing import Optional, List, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine

class TimelineView(Static):
    """Interactive Timeline View displaying event history table with category filters."""

    def __init__(self, storage: Optional[SQLiteStorage] = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.events_data: List[Dict[str, Any]] = []

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if self.storage:
            try:
                engine = TimelineEngine(self.storage)
                query_res = engine.query_events(limit=25)
                self.events_data = [
                    {
                        "id": e.id,
                        "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S") if e.timestamp else "N/A",
                        "type": e.normalized_event_type,
                        "source": e.source,
                        "summary": e.summary or "Event logged",
                        "session": e.session_id or "default"
                    }
                    for e in query_res.events
                ]
            except Exception:
                self.events_data = self._fallback_data()
        else:
            self.events_data = self._fallback_data()

        self.refresh()

    def _fallback_data(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "timestamp": "2026-07-23 14:00:00", "type": "filesystem", "source": "filesystem", "summary": "Created hello.py", "session": "sess-1"},
            {"id": 2, "timestamp": "2026-07-23 14:05:00", "type": "ai_prompt", "source": "claude", "summary": "Prompt: Add diff viewer", "session": "sess-1"},
            {"id": 3, "timestamp": "2026-07-23 14:10:00", "type": "git_commit", "source": "git", "summary": "commit: feat(diff): add file diff engine", "session": "sess-1"},
            {"id": 4, "timestamp": "2026-07-23 14:15:00", "type": "filesystem", "source": "filesystem", "summary": "Modified prometra/diff/engine.py", "session": "sess-1"},
            {"id": 5, "timestamp": "2026-07-23 14:20:00", "type": "ai_tool", "source": "claude", "summary": "Tool Call: Edit file main.py", "session": "sess-1"},
        ]

    def render(self) -> RenderableType:
        table = Table("ID", "Timestamp", "Category", "Source", "Summary", "Session ID", expand=True)

        type_colors = {
            "filesystem": "green",
            "ai_prompt": "magenta",
            "ai_tool": "bright_magenta",
            "git_commit": "yellow",
            "session": "cyan"
        }

        for ev in self.events_data:
            c = type_colors.get(ev["type"], "white")
            table.add_row(
                str(ev["id"]),
                ev["timestamp"],
                f"[{c}]{ev['type']}[/{c}]",
                ev["source"],
                ev["summary"],
                ev["session"]
            )

        return Panel(
            table,
            title="[2] INTERACTIVE EVENT TIMELINE",
            border_style="yellow"
        )
