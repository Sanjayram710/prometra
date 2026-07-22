from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from prometra.dashboard.metrics import DashboardMetrics

class DashboardRenderer:
    """Rich terminal renderer for Prometra Analytics Dashboard."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def render(self, metrics: DashboardMetrics):
        """Render full Rich terminal dashboard layout."""
        self.console.print(Panel(
            f"[bold white]Time Window:[/bold white] [bold cyan]{metrics.filter_label}[/bold cyan]",
            title="[bold cyan]Prometra Analytics Dashboard[/bold cyan]",
            border_style="cyan",
            expand=True
        ))

        # 1. Sessions & Overview
        sess = metrics.sessions
        dur = sess.total_duration_seconds
        dur_str = f"{dur // 3600}h {(dur % 3600) // 60}m" if dur >= 3600 else f"{dur // 60}m {dur % 60}s"
        long_str = f"{sess.longest_session_seconds // 60}m" if sess.longest_session_seconds >= 60 else f"{sess.longest_session_seconds}s"
        avg_str = f"{sess.avg_session_length_seconds // 60}m" if sess.avg_session_length_seconds >= 60 else f"{sess.avg_session_length_seconds}s"

        overview_table = Table(show_header=False, box=None, padding=(0, 2))
        overview_table.add_column("Metric", style="bold white")
        overview_table.add_column("Value", style="cyan")
        overview_table.add_row("Total Sessions", str(sess.total_sessions))
        overview_table.add_row("Total Duration", dur_str)
        overview_table.add_row("Longest Session", long_str)
        overview_table.add_row("Average Length", avg_str)

        self.console.print(Panel(overview_table, title="[bold white]📊 Sessions & Overview[/bold white]", border_style="blue"))

        # 2. Filesystem & Git
        fs_table = Table(show_header=False, box=None, padding=(0, 2))
        fs_table.add_column("Metric", style="bold white")
        fs_table.add_column("Value")
        fs_table.add_row("Files Created", f"[green]{metrics.filesystem.files_created}[/green]")
        fs_table.add_row("Files Modified", f"[yellow]{metrics.filesystem.files_modified}[/yellow]")
        fs_table.add_row("Files Deleted", f"[red]{metrics.filesystem.files_deleted}[/red]")
        fs_table.add_row("Git Commits", f"[blue]{metrics.git.total_commits} ({metrics.git.commits_per_day} / day)[/blue]")

        self.console.print(Panel(fs_table, title="[bold white]📝 Filesystem & Git Activity[/bold white]", border_style="green"))

        # 3. AI Interactions & Cost
        ai_table = Table(show_header=False, box=None, padding=(0, 2))
        ai_table.add_column("Metric", style="bold white")
        ai_table.add_column("Value")
        ai_table.add_row("AI Prompts", f"[bright_cyan]{metrics.ai.ai_prompts}[/bright_cyan]")
        ai_table.add_row("AI Responses", f"[green]{metrics.ai.ai_responses}[/green]")
        ai_table.add_row("Tool Calls", f"[yellow]{metrics.ai.tool_calls}[/yellow]")
        ai_table.add_row("Errors / Retries", f"[red]{metrics.ai.errors}[/red] / [yellow]{metrics.ai.retries}[/yellow]")
        ai_table.add_row("Total Tokens", f"[magenta]{metrics.ai.total_tokens} (In: {metrics.ai.prompt_tokens}, Out: {metrics.ai.completion_tokens})[/magenta]")
        ai_table.add_row("Estimated Cost", f"[bold green]${metrics.ai.estimated_cost:.4f}[/bold green]")
        ai_table.add_row("Connectors Used", f"[yellow]{', '.join(metrics.ai.connectors_used) if metrics.ai.connectors_used else 'None'}[/yellow]")

        self.console.print(Panel(ai_table, title="[bold white]🤖 AI Interactions & Costs[/bold white]", border_style="magenta"))

        # 4. Top Edited Files Table
        if metrics.filesystem.top_edited_files:
            file_table = Table(title="Top Edited Files", show_header=True, header_style="bold green")
            file_table.add_column("Rank", width=6, justify="center")
            file_table.add_column("File Path", style="cyan")
            file_table.add_column("Edits", justify="right", style="green")

            for idx, tf in enumerate(metrics.filesystem.top_edited_files, start=1):
                file_table.add_row(str(idx), tf.path, f"{tf.edits} edits")

            self.console.print(file_table)

        # 5. Top AI Models Table
        if metrics.ai.top_models:
            model_table = Table(title="Top AI Models", show_header=True, header_style="bold magenta")
            model_table.add_column("Rank", width=6, justify="center")
            model_table.add_column("Model Name", style="bright_cyan")
            model_table.add_column("Prompts", justify="right", style="magenta")

            for idx, tm in enumerate(metrics.ai.top_models, start=1):
                model_table.add_row(str(idx), tm.model_name, f"{tm.count} prompts")

            self.console.print(model_table)

        # 6. Top Active Hours
        if metrics.activity.top_active_hours:
            hours_str = ", ".join(f"{h:02d}:00" for h in metrics.activity.top_active_hours)
            self.console.print(Panel(f"[bold white]Peak Active Hours:[/bold white] [cyan]{hours_str}[/cyan]", border_style="cyan"))
