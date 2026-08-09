from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static

from prometra.compare.engine import CompareEngine
from prometra.storage.models import SessionModel
from prometra.storage.sqlite import SQLiteStorage


class CompareView(Static):
    """Interactive Session Comparison View rendering side-by-side session productivity and code churn metrics from SQLite DB."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.session_a: str | None = None
        self.session_b: str | None = None
        self.comp_data: dict[str, Any] = {}

    def on_mount(self) -> None:
        self.load_comparison()

    def _resolve_sessions(self) -> tuple[str | None, str | None]:
        if not self.storage:
            return None, None
        try:
            db = self.storage.get_session()
            sessions = (
                db.query(SessionModel)
                .order_by(SessionModel.start_ts.desc())
                .limit(2)
                .all()
            )
            db.close()
            if len(sessions) >= 2:
                return sessions[1].session_id, sessions[0].session_id
            elif len(sessions) == 1:
                return sessions[0].session_id, None
            return None, None
        except Exception:  # noqa: BLE001
            return None, None

    def load_comparison(
        self, sess_a: str | None = None, sess_b: str | None = None
    ) -> None:
        auto_a, auto_b = self._resolve_sessions()
        self.session_a = sess_a or self.session_a or auto_a
        self.session_b = sess_b or self.session_b or auto_b

        if self.storage and self.session_a and self.session_b:
            try:
                engine = CompareEngine(self.storage)
                res = engine.compare_sessions(
                    session_a=self.session_a, session_b=self.session_b
                )
                self.comp_data = {
                    "sess_a": res.session_a.session_id,
                    "sess_b": res.session_b.session_id,
                    "metrics_a": res.session_a.metrics,
                    "metrics_b": res.session_b.metrics,
                    "productivity_a": res.productivity_a,
                    "productivity_b": res.productivity_b,
                }
            except Exception:  # noqa: BLE001
                self.comp_data = {}
        else:
            self.comp_data = {}

        self.refresh()

    def render(self) -> RenderableType:
        d = self.comp_data

        if d:
            ma = d.get("metrics_a", {})
            mb = d.get("metrics_b", {})
            pa = d.get("productivity_a", {})
            pb = d.get("productivity_b", {})

            table = Table(
                "Metric",
                f"Session A ({d.get('sess_a')})",
                f"Session B ({d.get('sess_b')})",
                "Delta / Comparison",
                expand=True,
            )

            table.add_row(
                "Duration",
                f"{ma.get('duration_minutes', 0)} mins",
                f"{mb.get('duration_minutes', 0)} mins",
                f"{ma.get('duration_minutes', 0) - mb.get('duration_minutes', 0):+} mins",
            )
            table.add_row(
                "Files Created",
                str(ma.get("files_created", 0)),
                str(mb.get("files_created", 0)),
                f"{ma.get('files_created', 0) - mb.get('files_created', 0):+}",
            )
            table.add_row(
                "Files Modified",
                str(ma.get("files_modified", 0)),
                str(mb.get("files_modified", 0)),
                f"{ma.get('files_modified', 0) - mb.get('files_modified', 0):+}",
            )
            table.add_row(
                "Files Deleted",
                str(ma.get("files_deleted", 0)),
                str(mb.get("files_deleted", 0)),
                f"{ma.get('files_deleted', 0) - mb.get('files_deleted', 0):+}",
            )
            table.add_row(
                "Git Commits",
                str(ma.get("commits", 0)),
                str(mb.get("commits", 0)),
                f"{ma.get('commits', 0) - mb.get('commits', 0):+}",
            )
            table.add_row(
                "AI Interactions",
                str(ma.get("ai_events", 0)),
                str(mb.get("ai_events", 0)),
                f"{ma.get('ai_events', 0) - mb.get('ai_events', 0):+}",
            )
            table.add_row(
                "Events / Minute",
                f"{pa.get('events_per_min', 0):.2f}",
                f"{pb.get('events_per_min', 0):.2f}",
                f"{pa.get('events_per_min', 0) - pb.get('events_per_min', 0):+.2f}",
            )
            table.add_row(
                "Commits / Hour",
                f"{pa.get('commits_per_hour', 0):.1f}",
                f"{pb.get('commits_per_hour', 0):.1f}",
                f"{pa.get('commits_per_hour', 0) - pb.get('commits_per_hour', 0):+.1f}",
            )
        else:
            table = Table("Metric", "Session A", "Session B", "Status", expand=True)
            table.add_row(
                "-",
                "-",
                "-",
                "[dim]At least 2 recorded development sessions required for comparison.[/dim]",
            )

        return Panel(
            table, title="[6] SESSION COMPARISON ENGINE", border_style="yellow"
        )
