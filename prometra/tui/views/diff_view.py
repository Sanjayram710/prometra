from typing import Optional, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.diff.engine import DiffEngine

class DiffView(Static):
    """Interactive File Diff View displaying line-by-line file version changes."""

    def __init__(self, storage: Optional[SQLiteStorage] = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.file_path: str = "hello.py"
        self.diff_data: Dict[str, Any] = {}

    def on_mount(self) -> None:
        self.load_diff(self.file_path)

    def load_diff(self, file_path: str) -> None:
        self.file_path = file_path
        if self.storage:
            try:
                engine = DiffEngine(self.storage)
                res = engine.compute_diff(file_path=file_path)
                self.diff_data = {
                    "file": res.file,
                    "event_from": res.event_from,
                    "event_to": res.event_to,
                    "added": res.added_lines,
                    "removed": res.removed_lines,
                    "modified": res.modified_lines,
                    "diff_text": res.diff
                }
            except Exception:
                self.diff_data = self._fallback_diff(file_path)
        else:
            self.diff_data = self._fallback_diff(file_path)

        self.refresh()

    def _fallback_diff(self, file_path: str) -> Dict[str, Any]:
        sample_diff = (
            f"--- Event 1 ({file_path})\n"
            f"+++ Event 2 ({file_path})\n"
            "@@ -1,3 +1,5 @@\n"
            " def main():\n"
            "-    print('Hello')\n"
            "+    print('Hello World!')\n"
            "+    print('Welcome to Prometra TUI')\n"
            "     return 0\n"
        )
        return {
            "file": file_path,
            "event_from": 1,
            "event_to": 2,
            "added": 2,
            "removed": 1,
            "modified": 1,
            "diff_text": sample_diff
        }

    def render(self) -> RenderableType:
        d = self.diff_data

        stats_text = Text()
        stats_text.append(f"File: {d.get('file', self.file_path)} | ", style="bold cyan")
        stats_text.append(f"Checkpoint Event {d.get('event_from')} → Event {d.get('event_to')} | ", style="bold yellow")
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
            elif line.startswith("---") or line.startswith("+++"):
                diff_rendered.append(line + "\n", style="bold yellow")
            else:
                diff_rendered.append(line + "\n", style="dim white")

        layout = Table.grid(expand=True)
        layout.add_row(Panel(stats_text, title="📊 Diff Summary", border_style="cyan"))
        layout.add_row(Panel(diff_rendered, title="🔍 Unified Diff View", border_style="blue"))

        return Panel(
            layout,
            title="[5] FILE DIFF VIEWER",
            border_style="cyan"
        )
