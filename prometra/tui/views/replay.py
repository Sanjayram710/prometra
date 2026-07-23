from typing import Optional, List, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import RenderableType

from textual.widget import Widget
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.replay.engine import ReplayEngine

class ReplayView(Static):
    """Interactive Session Replay View with playback controls and step-by-step playback progress."""

    def __init__(self, storage: Optional[SQLiteStorage] = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.is_playing: bool = False
        self.current_step: int = 1
        self.total_steps: int = 10
        self.speed: str = "1x"
        self.current_event: Optional[Dict[str, Any]] = None

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self.current_event = {
            "step": self.current_step,
            "timestamp": "2026-07-23 14:15:00",
            "type": "FileModified",
            "source": "filesystem",
            "details": "Modified hello.py (+10 lines, -2 lines)",
            "diff_preview": '+ print("Hello World!")\n- print("Hello")'
        }
        self.refresh()

    def toggle_play(self) -> None:
        self.is_playing = not self.is_playing
        self.refresh()

    def step_forward(self) -> None:
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.refresh_data()

    def step_backward(self) -> None:
        if self.current_step > 1:
            self.current_step -= 1
            self.refresh_data()

    def render(self) -> RenderableType:
        # Progress Bar
        percent = int((self.current_step / max(self.total_steps, 1)) * 100)
        progress_text = Text()
        progress_text.append(f"Progress: [{self.current_step}/{self.total_steps}] ", style="bold cyan")
        progress_text.append(f"{'█' * (percent // 5)}{'░' * (20 - (percent // 5))} {percent}%\n", style="bold green")

        state_str = "▶ PLAYING" if self.is_playing else "⏸ PAUSED"
        controls_text = Text()
        controls_text.append(f"State: {state_str} | Speed: {self.speed} | Controls: [Space] Play/Pause | [→] Step Next | [←] Step Prev\n", style="bold yellow")

        ev = self.current_event or {}
        event_info = Text()
        event_info.append(f"Step {ev.get('step')}: [{ev.get('type')}] at {ev.get('timestamp')}\n", style="bold cyan")
        event_info.append(f"Source: {ev.get('source')} | Details: {ev.get('details')}\n\n", style="white")
        event_info.append("Code / Event Preview:\n", style="dim white")
        event_info.append(f"{ev.get('diff_preview')}\n", style="bold green")

        main_panel = Panel(
            event_info,
            title="🎞️ Step-by-Step Event Replay Stream",
            border_style="cyan"
        )

        layout = Table.grid(expand=True)
        layout.add_row(Panel(progress_text + controls_text, title="🎮 Replay Controls", border_style="green"))
        layout.add_row(main_panel)

        return Panel(
            layout,
            title="[3] SESSION REPLAY ENGINE",
            border_style="green"
        )
