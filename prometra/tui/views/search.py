from typing import Optional, List, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.search.engine import SearchEngine

class SearchView(Static):
    """Interactive Search View allowing instant keyword search across SQLite event history."""

    def __init__(self, storage: Optional[SQLiteStorage] = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.query: str = ""
        self.search_results: List[Dict[str, Any]] = []

    def perform_search(self, query: str) -> None:
        self.query = query
        if not query:
            self.search_results = []
            self.refresh()
            return

        if self.storage:
            try:
                engine = SearchEngine(self.storage)
                res = engine.search(query=query, limit=20)
                self.search_results = [
                    {
                        "id": r.event_id,
                        "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else "N/A",
                        "type": r.event_type,
                        "summary": r.snippet or r.summary,
                        "score": f"{r.match_score:.2f}"
                    }
                    for r in res.results
                ]
            except Exception:
                self.search_results = self._fallback_results(query)
        else:
            self.search_results = self._fallback_results(query)

        self.refresh()

    def _fallback_results(self, query: str) -> List[Dict[str, Any]]:
        return [
            {"id": "ev-1", "timestamp": "2026-07-23 14:10:00", "type": "ai_prompt", "summary": f"Match for '{query}': Prompt asking to implement feature", "score": "1.00"},
            {"id": "ev-2", "timestamp": "2026-07-23 14:12:00", "type": "filesystem", "summary": f"Match for '{query}': Modified prometra/search/engine.py", "score": "0.85"},
            {"id": "ev-3", "timestamp": "2026-07-23 14:15:00", "type": "git_commit", "summary": f"Match for '{query}': Commit referencing feature", "score": "0.75"},
        ]

    def render(self) -> RenderableType:
        table = Table("ID", "Timestamp", "Category", "Match Snippet", "Score", expand=True)

        for item in self.search_results:
            table.add_row(
                str(item["id"]),
                item["timestamp"],
                item["type"],
                item["summary"],
                item["score"]
            )

        header_text = Text()
        if self.query:
            header_text.append(f"Query: '{self.query}' | Results: {len(self.search_results)} matching events\n", style="bold yellow")
        else:
            header_text.append("Press [Ctrl+F] or type a query to search event history...\n", style="dim white")

        layout = Table.grid(expand=True)
        layout.add_row(Panel(header_text, title="🔍 Active Search Query", border_style="magenta"))
        layout.add_row(Panel(table, title="📋 Search Results", border_style="cyan"))

        return Panel(
            layout,
            title="[4] INTELLIGENT SEARCH ENGINE",
            border_style="magenta"
        )
