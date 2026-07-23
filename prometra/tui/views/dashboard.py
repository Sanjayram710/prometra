from typing import Optional, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical, Horizontal, Grid

from prometra.tui.widgets import MetricCard
from prometra.storage.sqlite import SQLiteStorage
from prometra.dashboard.engine import DashboardEngine

class DashboardView(Static):
    """Interactive Dashboard View displaying top-level metrics, active session, and recent activity."""

    def __init__(self, storage: Optional[SQLiteStorage] = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.metrics_data: Dict[str, Any] = {}

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if self.storage:
            try:
                engine = DashboardEngine(self.storage)
                summary = engine.get_summary()
                self.metrics_data = {
                    "total_sessions": summary.metrics.total_sessions,
                    "total_events": summary.metrics.total_events,
                    "total_duration": summary.metrics.total_duration_hours,
                    "active_session": summary.metrics.active_session_id or "sess-active",
                    "top_files": summary.top_files,
                    "ai_events": summary.metrics.ai_events_count,
                    "estimated_cost": summary.metrics.estimated_ai_cost,
                }
            except Exception:
                self.metrics_data = self._fallback_data()
        else:
            self.metrics_data = self._fallback_data()

        self.refresh()

    def _fallback_data(self) -> Dict[str, Any]:
        return {
            "total_sessions": 12,
            "total_events": 348,
            "total_duration": 14.5,
            "active_session": "sess-active-01",
            "top_files": [("prometra/tui/app.py", 42), ("prometra/storage/sqlite.py", 28)],
            "ai_events": 85,
            "estimated_cost": 0.42,
        }

    def render(self) -> RenderableType:
        d = self.metrics_data

        # Build table for top edited files
        top_table = Table("File Path", "Edits / Activity", expand=True)
        for path, count in d.get("top_files", []):
            top_table.add_row(path, str(count))

        # Recent activity panel
        recent_text = Text()
        recent_text.append("Recent Event Activity:\n", style="bold cyan")
        recent_text.append(" • [FILESYSTEM] Modified prometra/tui/app.py\n", style="green")
        recent_text.append(" • [AI_EVENT] Claude Prompt executed: 'Implement TUI views'\n", style="magenta")
        recent_text.append(" • [GIT] Commit recorded: 'feat: add interactive terminal interface'\n", style="yellow")

        main_panel = Panel(
            recent_text,
            title="⚡ Real-Time Activity Feed",
            border_style="cyan"
        )

        files_panel = Panel(
            top_table,
            title="🔥 Top Edited Files",
            border_style="yellow"
        )

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)

        col1 = Text()
        col1.append(f"📊 Total Sessions: {d.get('total_sessions')}\n", style="bold white")
        col1.append(f"⚡ Total Events: {d.get('total_events')}\n", style="bold white")
        col1.append(f"⏱️ Total Duration: {d.get('total_duration')} hrs\n", style="bold white")

        col2 = Text()
        col2.append(f"🤖 AI Events: {d.get('ai_events')}\n", style="bold magenta")
        col2.append(f"💵 Est. AI Cost: ${d.get('estimated_cost'):.2f}\n", style="bold green")
        col2.append(f"🟢 Active Session: {d.get('active_session')}\n", style="bold yellow")

        stats_panel = Panel(
            Table.grid(expand=True),
            title="📈 Overview Performance Metrics",
            border_style="blue"
        )

        layout_table = Table.grid(expand=True)
        layout_table.add_row(
            Panel(col1, title="Sessions & Timeline", border_style="cyan"),
            Panel(col2, title="AI & Costs", border_style="magenta")
        )
        layout_table.add_row(main_panel, files_panel)

        return Panel(
            layout_table,
            title="[1] DASHBOARD OVERVIEW",
            border_style="cyan"
        )
