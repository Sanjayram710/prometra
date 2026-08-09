from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from prometra.diff.engine import DiffEngine
from prometra.storage.models import FilesystemEventModel
from prometra.storage.sqlite import SQLiteStorage


class DiffView(Static):
    """Interactive File Diff View displaying real line-by-line file version changes from SQLite DB."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.file_path: str | None = None
        self.diff_data: dict[str, Any] = {}

    def on_mount(self) -> None:
        self.load_diff()

    def _resolve_recent_file(self) -> str | None:
        """Find the most recently recorded filesystem file path in database."""
        if not self.storage:
            return None
        try:
            db = self.storage.get_session()
            recent = (
                db.query(FilesystemEventModel)
                .order_by(FilesystemEventModel.timestamp.desc())
                .first()
            )
            path = (recent.normalized_relative_path or recent.path) if recent else None
            db.close()
            return path
        except Exception:  # noqa: BLE001
            return None

    def load_diff(self, file_path: str | None = None) -> None:
        target_path = file_path or self.file_path or self._resolve_recent_file()
        self.file_path = target_path

        if self.storage and target_path:
            try:
                engine = DiffEngine(self.storage)
                res = engine.compute_diff(file_path=target_path)
                self.diff_data = {
                    "file": res.file,
                    "event_from": res.event_from,
                    "event_to": res.event_to,
                    "added": res.added_lines,
                    "removed": res.removed_lines,
                    "modified": res.modified_lines,
                    "diff_text": res.diff,
                }
            except Exception:  # noqa: BLE001
                self.diff_data = {}
        else:
            self.diff_data = {}

        self.refresh()

    def render(self) -> RenderableType:
        d = self.diff_data

        if d and d.get("diff_text"):
            stats_text = Text()
            stats_text.append(
                f"File: {d.get('file', self.file_path)} | ", style="bold cyan"
            )
            stats_text.append(
                f"Event {d.get('event_from')} → Event {d.get('event_to')} | ",
                style="bold yellow",
            )
            stats_text.append(f" +{d.get('added', 0)} ", style="bold green")
            stats_text.append(f" -{d.get('removed', 0)} ", style="bold red")
            stats_text.append(f" ~{d.get('modified', 0)} modified", style="bold blue")

            diff_rendered = Text()
            raw_text = d.get("diff_text", "")
            for line in raw_text.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    diff_rendered.append(line + "\n", style="green")
                elif line.startswith("-") and not line.startswith("---"):
                    diff_rendered.append(line + "\n", style="red")
                elif line.startswith("@"):
                    diff_rendered.append(line + "\n", style="bold cyan")
                elif line.startswith(("---", "+++")):
                    diff_rendered.append(line + "\n", style="bold yellow")
                else:
                    diff_rendered.append(line + "\n", style="dim white")
        else:
            stats_text = Text(
                f"File: {self.file_path or 'N/A'} | Status: No Diffs Recorded",
                style="dim white",
            )
            diff_rendered = Text(
                "No recorded line diffs available for this file in database history.\n",
                style="dim white",
            )

        layout = Table.grid(expand=True)
        layout.add_row(Panel(stats_text, title="📊 Diff Summary", border_style="cyan"))
        layout.add_row(
            Panel(diff_rendered, title="🔍 Unified Diff View", border_style="blue")
        )

        return Panel(layout, title="[5] FILE DIFF VIEWER", border_style="cyan")
