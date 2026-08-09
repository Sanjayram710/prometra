from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from prometra.dashboard.engine import DashboardEngine
from prometra.storage.models import SessionModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter


class DashboardView(Static):
    """Interactive Dashboard View displaying real top-level metrics, active session, and live activity feed from SQLite DB."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.metrics_data: dict[str, Any] = {}
        self.recent_events: list[dict[str, Any]] = []

    def on_mount(self) -> None:
        self.refresh_data()

    def _get_active_session_id(self) -> str:
        if not self.storage:
            return "No Active Session"
        try:
            db = self.storage.get_session()
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

    def refresh_data(self) -> None:
        if self.storage:
            try:
                # 1. Dashboard summary metrics
                engine = DashboardEngine(self.storage)
                summary = engine.compute_metrics()

                top_files = (
                    [(tf.path, tf.edits) for tf in summary.filesystem.top_edited_files]
                    if summary.filesystem.top_edited_files
                    else []
                )

                total_events = (
                    summary.filesystem.files_created
                    + summary.filesystem.files_modified
                    + summary.filesystem.files_deleted
                    + summary.git.total_commits
                    + summary.ai.ai_prompts
                )

                self.metrics_data = {
                    "total_sessions": summary.sessions.total_sessions,
                    "total_events": total_events,
                    "total_duration": round(
                        summary.sessions.total_duration_seconds / 3600.0, 2
                    ),
                    "active_session": self._get_active_session_id(),
                    "top_files": top_files,
                    "ai_events": summary.ai.ai_prompts,
                    "estimated_cost": summary.ai.estimated_cost,
                }
            except Exception:  # noqa: BLE001
                import traceback

                traceback.print_exc()
                self.metrics_data = self._empty_metrics()

            try:
                # 2. Live activity feed from TimelineEngine
                tl_engine = TimelineEngine(self.storage)
                query_res = tl_engine.query_events(filters=TimelineFilter(limit=5))
                self.recent_events = [
                    {
                        "type": e.normalized_event_type.upper(),
                        "summary": e.summary or "Event logged",
                        "timestamp": e.timestamp.strftime("%H:%M:%S")
                        if e.timestamp
                        else "N/A",
                    }
                    for e in query_res
                ]
            except Exception:  # noqa: BLE001
                self.recent_events = []
        else:
            self.metrics_data = self._empty_metrics()
            self.recent_events = []

        self.refresh()

    def _empty_metrics(self) -> dict[str, Any]:
        return {
            "total_sessions": 0,
            "total_events": 0,
            "total_duration": 0.0,
            "active_session": "No Active Session",
            "top_files": [],
            "ai_events": 0,
            "estimated_cost": 0.0,
        }

    def render(self) -> RenderableType:
        d = self.metrics_data or self._empty_metrics()

        # Build table for top edited files
        top_table = Table("File Path", "Edits / Activity", expand=True)
        top_files = d.get("top_files", [])
        if top_files:
            for path, count in top_files:
                top_table.add_row(path, str(count))
        else:
            top_table.add_row("[dim]No file edits recorded[/dim]", "0")

        # Recent activity panel
        recent_text = Text()
        recent_text.append("Recent Event Activity:\n", style="bold cyan")
        if self.recent_events:
            category_colors = {
                "FILESYSTEM": "green",
                "AI_PROMPT": "magenta",
                "AI_TOOL": "bright_magenta",
                "GIT": "yellow",
                "SESSION": "cyan",
            }
            for ev in self.recent_events:
                color = category_colors.get(ev["type"], "white")
                recent_text.append(f" • [{ev['type']}] ", style=color)
                recent_text.append(f"{ev['summary']} ", style="white")
                recent_text.append(f"({ev['timestamp']})\n", style="dim white")
        else:
            recent_text.append(
                " • [dim]No activity recorded in project history.[/dim]\n",
                style="dim white",
            )

        main_panel = Panel(
            recent_text, title="⚡ Real-Time Activity Feed", border_style="cyan"
        )

        files_panel = Panel(
            top_table, title="🔥 Top Edited Files", border_style="yellow"
        )

        col1 = Text()
        col1.append(
            f"📊 Total Sessions: {d.get('total_sessions', 0)}\n", style="bold white"
        )
        col1.append(
            f"⚡ Total Events: {d.get('total_events', 0)}\n", style="bold white"
        )
        col1.append(
            f"⏱️ Total Duration: {d.get('total_duration', 0.0):.2f} hrs\n",
            style="bold white",
        )

        col2 = Text()
        col2.append(f"🤖 AI Events: {d.get('ai_events', 0)}\n", style="bold magenta")
        col2.append(
            f"💵 Est. AI Cost: ${d.get('estimated_cost', 0.0):.4f}\n",
            style="bold green",
        )
        col2.append(
            f"🟢 Active Session: {d.get('active_session', 'No Active Session')}\n",
            style="bold yellow",
        )

        layout_table = Table.grid(expand=True)
        layout_table.add_row(
            Panel(col1, title="Sessions & Timeline", border_style="cyan"),
            Panel(col2, title="AI & Costs", border_style="magenta"),
        )
        layout_table.add_row(main_panel, files_panel)

        return Panel(layout_table, title="[1] DASHBOARD OVERVIEW", border_style="cyan")
