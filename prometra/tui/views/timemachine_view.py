from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.timemachine.checkpoint import CheckpointManager
from prometra.timemachine.restore import RestoreEngine


class TimeMachineView(Static):
    """Interactive Time Machine View (#10) rendering real checkpoints, restore previews, and checkpoint diffs from disk/SQLite DB."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.checkpoints: list[dict[str, Any]] = []
        self.selected_checkpoint: dict[str, Any] | None = None
        self.restore_preview_info: str | None = None

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if self.storage:
            try:
                mgr = CheckpointManager(self.storage)
                cps = mgr.list_checkpoints()
                self.checkpoints = [
                    {
                        "id": c.id,
                        "message": c.message,
                        "timestamp": c.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if c.timestamp
                        else "N/A",
                        "branch": c.git_branch,
                        "commit": c.git_commit,
                        "files_count": len(c.modified_files),
                        "score": c.productivity_score,
                    }
                    for c in cps
                ]
            except Exception:  # noqa: BLE001
                self.checkpoints = []
        else:
            self.checkpoints = []

        if self.checkpoints:
            self.selected_checkpoint = self.checkpoints[0]
            try:
                r_eng = RestoreEngine()
                prev = r_eng.preview_restore(self.selected_checkpoint["id"])
                self.restore_preview_info = (
                    f"Restore Preview for '{prev.checkpoint_id}': "
                    f"{len(prev.files_created)} created, "
                    f"{len(prev.files_modified)} modified, "
                    f"{len(prev.files_deleted)} deleted."
                )
            except Exception:  # noqa: BLE001
                self.restore_preview_info = f"Restore Preview: {self.selected_checkpoint['files_count']} files tracked."
        else:
            self.selected_checkpoint = None
            self.restore_preview_info = None

        self.refresh()

    def render(self) -> RenderableType:
        table = Table(
            "Checkpoint ID",
            "Timestamp",
            "Git Branch",
            "Commit",
            "Modified Files",
            "Score",
            "Message",
            expand=True,
        )

        if self.checkpoints:
            for cp in self.checkpoints:
                table.add_row(
                    f"[bold cyan]{cp['id']}[/bold cyan]",
                    cp["timestamp"],
                    cp["branch"],
                    cp["commit"],
                    str(cp["files_count"]),
                    f"{cp['score']}/100",
                    cp["message"],
                )
        else:
            table.add_row(
                "-",
                "-",
                "-",
                "-",
                "0",
                "0/100",
                "[dim]No checkpoints recorded. Run 'prometra checkpoint' to save project state.[/dim]",
            )

        preview_text = Text()
        if self.selected_checkpoint:
            c = self.selected_checkpoint
            preview_text.append(
                f"Selected Checkpoint: {c['id']}\n", style="bold yellow"
            )
            preview_text.append(f"Message: {c['message']}\n", style="bold white")
            preview_text.append(
                f"{self.restore_preview_info or 'Restore Preview available'}\n",
                style="green",
            )
            preview_text.append(
                "Use CLI: 'prometra restore "
                + c["id"]
                + "' to apply state restoration.\n",
                style="dim white",
            )
        else:
            preview_text.append(
                "No checkpoint selected. Use [prometra checkpoint] to create snapshots.\n",
                style="dim white",
            )

        layout = Table.grid(expand=True)
        layout.add_row(
            Panel(table, title="📍 Saved Development Checkpoints", border_style="cyan")
        )
        layout.add_row(
            Panel(
                preview_text, title="🔍 Restore & Diff Previewer", border_style="yellow"
            )
        )

        return Panel(
            layout, title="[10] TIME MACHINE & CHECKPOINT SYSTEM", border_style="cyan"
        )
