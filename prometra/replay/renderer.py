from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from prometra.storage.models import TimelineEventModel
from prometra.replay.formatter import ReplayFormatter

class ReplayRenderer:
    """Rich terminal renderer for Prometra session replay."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def get_event_color(self, event_type: str) -> str:
        net = (event_type or "").lower()
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
        elif "ai" in net:
            return "magenta"
        return "white"

    def render_session_header(self, session_info: Dict[str, Any]):
        """Render session header panel."""
        sess_id = session_info.get("session_id", "Unknown")
        dur = session_info.get("duration_seconds", 0)
        dur_str = f"{dur // 60}m {dur % 60}s" if dur >= 60 else f"{dur}s"
        total = session_info.get("total_events", 0)
        status = session_info.get("status", "completed")

        text = (
            f"[bold cyan]Session[/bold cyan]: [white]{sess_id}[/white]\n"
            f"[bold white]Duration[/bold white]: [white]{dur_str}[/white] | "
            f"[bold white]Events[/bold white]: [cyan]{total}[/cyan] | "
            f"[bold white]Status[/bold white]: [green]{status}[/green]"
        )
        self.console.print(Panel(text, title="[bold cyan]Prometra Session Replay[/bold cyan]", border_style="cyan", expand=True))

    def render_event(self, e: TimelineEventModel, step_number: Optional[int] = None, total_steps: Optional[int] = None):
        """Render a single replay event line."""
        icon = ReplayFormatter.get_event_icon(e.normalized_event_type)
        color = self.get_event_color(e.normalized_event_type)

        ts_str = str(e.timestamp).split(" ")[-1][:8] if e.timestamp and " " in str(e.timestamp) else str(e.timestamp or "")
        cat = e.normalized_event_type or "Event"
        src = e.source or "system"
        summary = e.summary or ""

        step_prefix = f"[dim][{step_number}/{total_steps}][/dim] " if step_number and total_steps else ""

        line = (
            f"{step_prefix}[dim]{ts_str}[/dim] {icon} [{color} bold]{cat}[/{color} bold] "
            f"[dim]({src})[/dim] [{color}]{summary}[/{color}]"
        )
        self.console.print(line)

    def render_footer(self, session_info: Dict[str, Any]):
        """Render session complete footer."""
        sess_id = session_info.get("session_id", "")
        self.console.print(Panel(f"[bold green][DONE] Replay finished for session #{sess_id}[/bold green]", border_style="green", expand=True))
