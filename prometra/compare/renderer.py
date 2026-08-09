
from rich.console import Console

from prometra.compare.models import CompareResult


class CompareRenderer:
    """Renderer for displaying visual session comparison in terminal."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def render(self, result: CompareResult) -> None:
        """Render formatted terminal output for CompareResult."""
        divider = "-" * 50
        vs_divider = f"{'-' * 12} VS {'-' * 12}"

        self.console.print(divider)
        self.console.print("[bold cyan]Session Comparison[/bold cyan]")
        self.console.print()

        # Session A
        self.console.print(f"[bold]Session A[/bold] ([dim]{result.session_a}[/dim])")
        self.console.print()
        self.console.print("Duration")
        self.console.print(f"{result.stats_a.duration_minutes} min")
        self.console.print()
        self.console.print("Files Modified")
        self.console.print(str(result.stats_a.files_modified))
        self.console.print()
        self.console.print("Git Commits")
        self.console.print(str(result.stats_a.git_commits))
        self.console.print()
        self.console.print("AI Events")
        self.console.print(str(result.stats_a.ai_events))
        self.console.print()

        # VS Divider
        self.console.print(vs_divider)
        self.console.print()

        # Session B
        self.console.print(f"[bold]Session B[/bold] ([dim]{result.session_b}[/dim])")
        self.console.print()
        self.console.print("Duration")
        self.console.print(f"{result.stats_b.duration_minutes} min")
        self.console.print()
        self.console.print("Files Modified")
        self.console.print(str(result.stats_b.files_modified))
        self.console.print()
        self.console.print("Git Commits")
        self.console.print(str(result.stats_b.git_commits))
        self.console.print()
        self.console.print("AI Events")
        self.console.print(str(result.stats_b.ai_events))
        self.console.print()

        # Difference
        self.console.print("[bold]Difference[/bold]")
        self.console.print()

        # Duration diff
        dur_sign = "+" if result.duration_seconds_difference >= 0 else ""
        dur_str = f"{dur_sign}{result.stats_b.duration_minutes - result.stats_a.duration_minutes} min"
        if result.duration_seconds_difference > 0:
            self.console.print(f"[green]{dur_str}[/green]")
        elif result.duration_seconds_difference < 0:
            self.console.print(f"[red]{dur_str}[/red]")
        else:
            self.console.print(dur_str)

        # Files diff
        tot_files_diff = (
            result.files_modified_difference
            + result.files_created_difference
            - result.files_deleted_difference
        )
        file_sign = "+" if tot_files_diff >= 0 else ""
        file_str = f"{file_sign}{tot_files_diff} files"
        if tot_files_diff > 0:
            self.console.print(f"[green]{file_str}[/green]")
        elif tot_files_diff < 0:
            self.console.print(f"[red]{file_str}[/red]")
        else:
            self.console.print(file_str)

        # Git commit diff
        commit_sign = "+" if result.git_commit_difference >= 0 else ""
        commit_str = f"{commit_sign}{result.git_commit_difference} commits"
        if result.git_commit_difference > 0:
            self.console.print(f"[green]{commit_str}[/green]")
        elif result.git_commit_difference < 0:
            self.console.print(f"[red]{commit_str}[/red]")
        else:
            self.console.print(commit_str)

        # AI event diff
        ai_sign = "+" if result.ai_event_difference >= 0 else ""
        ai_str = f"{ai_sign}{result.ai_event_difference} AI events"
        if result.ai_event_difference > 0:
            self.console.print(f"[green]{ai_str}[/green]")
        elif result.ai_event_difference < 0:
            self.console.print(f"[red]{ai_str}[/red]")
        else:
            self.console.print(ai_str)

        self.console.print(divider)
