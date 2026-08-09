from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from prometra.search.engine import SearchEngine
from prometra.storage.sqlite import SQLiteStorage


class SearchView(Static):
    """Interactive Search View allowing instant keyword search across SQLite event history."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.query: str = ""
        self.search_results: list[dict[str, Any]] = []

    def perform_search(self, query: str) -> None:
        self.query = query
        if not query:
            self.search_results = []
            self.refresh()
            return

        if self.storage:
            try:
                engine = SearchEngine(self.storage)
                res = engine.search_events(query=query, limit=20)
                self.search_results = [
                    {
                        "id": r.event_id,
                        "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if r.timestamp
                        else "N/A",
                        "type": r.category,
                        "summary": r.summary,
                        "score": "1.00",
                    }
                    for r in res.results
                ]
            except Exception:  # noqa: BLE001
                self.search_results = []
        else:
            self.search_results = []

        self.refresh()

    def render(self) -> RenderableType:
        table = Table(
            "ID", "Timestamp", "Category", "Match Snippet", "Score", expand=True
        )

        if self.search_results:
            for item in self.search_results:
                table.add_row(
                    str(item["id"]),
                    item["timestamp"],
                    item["type"],
                    item["summary"],
                    item["score"],
                )
        elif self.query:
            table.add_row(
                "-",
                "-",
                "-",
                f"[dim]No matching events found for '{self.query}'.[/dim]",
                "-",
            )
        else:
            table.add_row(
                "-",
                "-",
                "-",
                "[dim]Enter a search query to inspect recorded events.[/dim]",
                "-",
            )

        header_text = Text()
        if self.query:
            header_text.append(
                f"Query: '{self.query}' | Results: {len(self.search_results)} matching events\n",
                style="bold yellow",
            )
        else:
            header_text.append(
                "Press [Ctrl+F] or type a query to search event history...\n",
                style="dim white",
            )

        layout = Table.grid(expand=True)
        layout.add_row(
            Panel(header_text, title="🔍 Active Search Query", border_style="magenta")
        )
        layout.add_row(Panel(table, title="📋 Search Results", border_style="cyan"))

        return Panel(
            layout, title="[4] INTELLIGENT SEARCH ENGINE", border_style="magenta"
        )
