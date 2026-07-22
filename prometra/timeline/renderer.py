from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style
from prometra.storage.models import TimelineEventModel
from prometra.timeline.summary import SummaryMetrics

class TimelineRenderer:
    """Rich terminal renderer for Prometra timeline views, tables, summaries, and groups."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def get_category_color(self, category: str, source: str = "") -> str:
        cat_lower = (category or "").lower()
        src_lower = (source or "").lower()

        if "error" in cat_lower or "error" in src_lower:
            return "red"
        elif "filesystem" in cat_lower:
            return "green"
        elif "git" in cat_lower:
            return "blue"
        elif "ai" in cat_lower or cat_lower in ["promptsubmitted", "responsereceived", "toolinvocation", "modelselected", "contextbuilt", "tokenusage", "latencymeasured"]:
            return "magenta"
        elif "connector" in cat_lower or "claude" in src_lower:
            return "yellow"
        elif "session" in cat_lower:
            return "cyan"
        return "white"

    def render_table(self, events: List[TimelineEventModel], title: str = "Prometra Interactive Timeline"):
        """Render timeline events in a styled Rich table."""
        if not events:
            self.console.print(Panel("[yellow]No timeline events found matching criteria.[/yellow]", title=title))
            return

        table = Table(title=title, show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Timestamp", style="dim", width=22)
        table.add_column("Category", width=14)
        table.add_column("Source", width=12)
        table.add_column("Description")
        table.add_column("Session", width=14)
        table.add_column("Connector", width=12)

        for e in events:
            cat = e.normalized_event_type or "system"
            src = e.source or "system"
            color = self.get_category_color(cat, src)

            ts_str = str(e.timestamp) if e.timestamp else ""
            cat_styled = f"[{color}]{cat}[/{color}]"
            src_styled = f"[{color}]{src}[/{color}]"
            desc = e.summary or ""
            sess_styled = f"[cyan]{e.session_id or ''}[/cyan]"
            conn = e.actor_tool or e.source or ""
            conn_styled = f"[yellow]{conn}[/yellow]" if conn else ""

            table.add_row(ts_str, cat_styled, src_styled, desc, sess_styled, conn_styled)

        self.console.print(table)

    def render_summary(self, summary: SummaryMetrics):
        """Render summary dashboard using Rich Panels and Tables."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="bold white")
        table.add_column("Value", style="cyan")

        table.add_row("Sessions", str(summary.sessions_count))
        table.add_row("Files Modified", f"[green]{summary.files_modified}[/green]")
        table.add_row("Git Commits", f"[blue]{summary.git_commits}[/blue]")
        table.add_row("AI Events", f"[magenta]{summary.ai_events}[/magenta]")
        table.add_row("Connectors Used", f"[yellow]{', '.join(summary.connectors_used) if summary.connectors_used else 'None'}[/yellow]")
        table.add_row("Total Events", f"[bold white]{summary.total_events}[/bold white]")

        panel = Panel(table, title="[bold cyan]Timeline Summary[/bold cyan]", border_style="cyan", expand=False)
        self.console.print(panel)

    def render_grouped(self, grouped_sessions: List[Dict[str, Any]]):
        """Render events grouped by session with session metrics."""
        if not grouped_sessions:
            self.console.print(Panel("[yellow]No session data available.[/yellow]", title="Grouped Timeline"))
            return

        for group in grouped_sessions:
            sess_id = group["session_id"]
            duration = group["duration_seconds"]
            files = group["files_changed"]
            commits = group["git_commits"]
            ai_count = group["ai_events"]
            events = group["events"]

            header_text = (
                f"[bold cyan]Session #{sess_id}[/bold cyan]\n"
                f"Duration: [white]{duration}s[/white] | "
                f"Files changed: [green]{files}[/green] | "
                f"Git commits: [blue]{commits}[/blue] | "
                f"AI events: [magenta]{ai_count}[/magenta]"
            )
            self.console.print(Panel(header_text, border_style="blue", expand=True))
            self.render_table(events, title=f"Events for Session #{sess_id}")
            self.console.print("")
