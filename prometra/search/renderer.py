import re

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prometra.search.models import SearchResultSet


class SearchRenderer:
    """Rich terminal renderer for Prometra search results with keyword highlighting."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def _get_category_color(self, category: str) -> str:
        net = (category or "").lower()
        if "error" in net or "fail" in net:
            return "red"
        elif "prompt" in net:
            return "bright_cyan"
        elif "response" in net:
            return "green"
        elif "tool" in net:
            return "yellow"
        elif "filesystem" in net or "file" in net:
            return "green"
        elif "git" in net:
            return "blue"
        elif "session" in net:
            return "cyan"
        return "white"

    def _highlight_query(self, text: str, query: str) -> str:
        """Safely highlight query term in text."""
        if not query or not text:
            return text
        try:
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            return pattern.sub(
                lambda m: f"[bold yellow]{m.group(0)}[/bold yellow]", text
            )
        except (re.error, TypeError, ValueError):
            return text

    def render(self, result_set: SearchResultSet):
        """Render full Rich terminal search UI."""
        header_text = (
            f'[bold white]Query:[/bold white] [bold cyan]"{result_set.query}"[/bold cyan] | '
            f"[bold white]Total Results:[/bold white] [green]{result_set.total_results}[/green] | "
            f"[bold white]Execution Time:[/bold white] [yellow]{result_set.execution_time_ms} ms[/yellow]"
        )
        self.console.print(
            Panel(
                header_text,
                title="[bold cyan]Prometra Search Engine[/bold cyan]",
                border_style="cyan",
            )
        )

        if result_set.applied_filters:
            filter_tags = " | ".join(
                f"[bold white]{k}:[/bold white] [yellow]{v}[/yellow]"
                for k, v in result_set.applied_filters.items()
            )
            self.console.print(
                Panel(
                    filter_tags,
                    title="[bold white]Applied Filters[/bold white]",
                    border_style="blue",
                )
            )

        if not result_set.results:
            self.console.print(
                "[yellow]No matching events found for your search query.[/yellow]"
            )
            return

        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Timestamp", style="dim", width=12)
        table.add_column("Category", width=16)
        table.add_column("Source", style="dim", width=12)
        table.add_column("Session ID", style="dim", width=10)
        table.add_column("Summary / Details")

        for item in result_set.results:
            ts_str = (
                str(item.timestamp).split(" ")[-1][:8]
                if item.timestamp and " " in str(item.timestamp)
                else str(item.timestamp or "")
            )
            color = self._get_category_color(item.category)
            cat_str = f"[{color} bold]{item.category}[/{color} bold]"
            sess_str = item.session_id[:8] if item.session_id else "none"

            highlighted_summary = self._highlight_query(item.summary, result_set.query)

            table.add_row(
                ts_str, cat_str, item.source or "system", sess_str, highlighted_summary
            )

        self.console.print(table)
