from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from prometra.intelligence.analyzer import IntelligenceAnalyzer
from prometra.storage.sqlite import SQLiteStorage


class InsightsView(Static):
    """Interactive Insights View (#9) rendering real AI session intelligence, productivity score, patterns, and recommendations from SQLite DB."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.insights_data: dict[str, Any] | None = None

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if self.storage:
            try:
                analyzer = IntelligenceAnalyzer(self.storage)
                res = analyzer.analyze_session()
                self.insights_data = {
                    "score": res.productivity.score,
                    "stars": res.productivity.stars,
                    "category": res.classification.primary_category,
                    "duration": res.summary.duration_minutes,
                    "events": res.summary.total_events,
                    "files_mod": res.summary.files_modified,
                    "commits": res.summary.git_commits,
                    "prompts": res.ai_usage.total_prompts,
                    "cost": res.ai_usage.estimated_cost,
                    "patterns": [p.name for p in res.patterns],
                    "recommendations": [
                        f"• {r.title}: {r.action_item}" for r in res.recommendations
                    ],
                }
            except Exception:  # noqa: BLE001
                import traceback

                traceback.print_exc()
                self.insights_data = None
        else:
            self.insights_data = None

        self.refresh()

    def render(self) -> RenderableType:
        if self.insights_data:
            d = self.insights_data

            # Score & Category Banner
            score_text = Text()
            score_text.append("PRODUCTIVITY SCORE: ", style="bold white")
            score_text.append(f"{d.get('score')} / 100  ", style="bold green")
            score_text.append(f"{d.get('stars')}  |  ", style="bold yellow")
            score_text.append("CLASSIFICATION: ", style="bold white")
            score_text.append(f"[{d.get('category')}]\n", style="bold cyan")

            score_panel = Panel(
                score_text, title="🌟 Session Intelligence Rating", border_style="green"
            )

            # Summary Grid Table
            summary_table = Table("Metric", "Value", "Metric", "Value", expand=True)
            summary_table.add_row(
                "Duration",
                f"{d.get('duration'):.1f} mins",
                "Git Commits",
                str(d.get("commits")),
            )
            summary_table.add_row(
                "Total Events",
                str(d.get("events")),
                "AI Prompts",
                str(d.get("prompts")),
            )
            summary_table.add_row(
                "Files Modified",
                str(d.get("files_mod")),
                "Est. AI Cost",
                f"${d.get('cost'):.4f}",
            )

            summary_panel = Panel(
                summary_table, title="📊 Session Metrics", border_style="cyan"
            )

            # Patterns & Recommendations
            recs_text = Text()
            if d.get("patterns"):
                recs_text.append("Detected Patterns: ", style="bold yellow")
                recs_text.append(
                    f"{', '.join(d.get('patterns', []))}\n\n", style="white"
                )

            recs_text.append("Actionable Recommendations:\n", style="bold cyan")
            for rec in d.get("recommendations", []):
                recs_text.append(f"{rec}\n", style="dim white")

            recs_panel = Panel(
                recs_text,
                title="💡 Intelligence Insights & Recommendations",
                border_style="yellow",
            )

            layout = Table.grid(expand=True)
            layout.add_row(score_panel)
            layout.add_row(summary_panel)
            layout.add_row(recs_panel)
        else:
            empty_text = Text(
                "No recorded sessions found for session intelligence analysis.\n",
                style="dim white",
            )
            layout = Panel(
                empty_text,
                title="🌟 Session Intelligence Rating",
                border_style="dim white",
            )

        return Panel(
            layout,
            title="[9] AI SESSION INTELLIGENCE & PRODUCTIVITY",
            border_style="cyan",
        )
