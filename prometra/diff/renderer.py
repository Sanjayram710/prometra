
from rich.console import Console

from prometra.diff.models import DiffResult


class DiffRenderer:
    """Renderer for displaying visual diff output in terminal."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def render(self, result: DiffResult) -> None:
        """Render formatted terminal output for DiffResult."""
        divider = "-" * 48

        self.console.print(divider)
        self.console.print("[bold]File[/bold]")
        self.console.print(result.file)
        self.console.print()
        self.console.print("[bold]Compared[/bold]")
        self.console.print(f"Event {result.event_from}")
        self.console.print("↓")
        self.console.print(f"Event {result.event_to}")
        self.console.print()

        if not result.diff.strip():
            self.console.print(
                "[yellow]No diff available (files are identical).[/yellow]"
            )
        else:
            diff_lines = result.diff.splitlines()
            for line in diff_lines:
                if line.startswith(("---", "+++")):
                    self.console.print(f"[bold cyan]{line}[/bold cyan]")
                elif line.startswith("@@"):
                    self.console.print(f"[cyan]{line}[/cyan]")
                elif line.startswith("-"):
                    self.console.print(f"[red]{line}[/red]")
                elif line.startswith("+"):
                    self.console.print(f"[green]{line}[/green]")
                else:
                    self.console.print(line)

        self.console.print(divider)
