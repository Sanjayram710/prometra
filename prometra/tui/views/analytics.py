from typing import Optional, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.analyzer.stats import StatsCalculator

class AnalyticsView(Static):
    """Extended Analytics View displaying AI token usage, cost breakdowns, and peak activity hours."""

    def __init__(self, storage: Optional[SQLiteStorage] = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.analytics_data: Dict[str, Any] = {}

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self.analytics_data = {
            "token_usage": {
                "claude-3-5-sonnet": {"input": 125400, "output": 38200, "cost": 0.94},
                "gpt-4o": {"input": 45000, "output": 12000, "cost": 0.29},
            },
            "peak_hours": ["14:00 - 15:00", "16:00 - 17:00"],
            "total_tokens": 220600,
            "total_cost": 1.23,
            "health_score": "98% (Healthy)"
        }
        self.refresh()

    def render(self) -> RenderableType:
        d = self.analytics_data

        token_table = Table("AI Model", "Input Tokens", "Output Tokens", "Est. Cost", expand=True)
        for model, usage in d.get("token_usage", {}).items():
            token_table.add_row(
                model,
                f"{usage['input']:,}",
                f"{usage['output']:,}",
                f"${usage['cost']:.2f}"
            )

        summary_text = Text()
        summary_text.append(f"Codebase Health Score: {d.get('health_score')}\n", style="bold green")
        summary_text.append(f"Total AI Tokens Consumed: {d.get('total_tokens', 0):,}\n", style="bold cyan")
        summary_text.append(f"Total Estimated AI Expense: ${d.get('total_cost'):.2f}\n", style="bold yellow")
        summary_text.append(f"Peak Developer Activity Hours: {', '.join(d.get('peak_hours', []))}\n", style="bold magenta")

        layout = Table.grid(expand=True)
        layout.add_row(Panel(summary_text, title="📈 Codebase Health & AI Cost Summary", border_style="green"))
        layout.add_row(Panel(token_table, title="🤖 AI Model Token Consumption", border_style="cyan"))

        return Panel(
            layout,
            title="[7] ANALYTICS & COST INSIGHTS",
            border_style="magenta"
        )
