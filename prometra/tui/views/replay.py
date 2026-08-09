from typing import Any

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter


class ReplayView(Static):
    """Interactive Session Replay View with step-by-step playback progress over real timeline events."""

    def __init__(self, storage: SQLiteStorage | None = None, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.is_playing: bool = False
        self.current_step: int = 1
        self.speed: str = "1x"
        self.events_list: list[dict[str, Any]] = []

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if self.storage:
            try:
                engine = TimelineEngine(self.storage)
                query_res = engine.query_events(filters=TimelineFilter(limit=50))
                self.events_list = [
                    {
                        "step": i + 1,
                        "id": e.id,
                        "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if e.timestamp
                        else "N/A",
                        "type": e.normalized_event_type,
                        "source": e.source,
                        "summary": e.summary or "Event logged",
                        "session": e.session_id or "default",
                    }
                    for i, e in enumerate(query_res)
                ]
            except Exception:  # noqa: BLE001
                self.events_list = []
        else:
            self.events_list = []

        if self.events_list and self.current_step > len(self.events_list):
            self.current_step = 1

        self.refresh()

    def toggle_play(self) -> None:
        self.is_playing = not self.is_playing
        self.refresh()

    def step_forward(self) -> None:
        if self.current_step < len(self.events_list):
            self.current_step += 1
            self.refresh()

    def step_backward(self) -> None:
        if self.current_step > 1:
            self.current_step -= 1
            self.refresh()

    def render(self) -> RenderableType:
        total_steps = len(self.events_list)

        if total_steps > 0:
            step_idx = max(0, min(self.current_step - 1, total_steps - 1))
            ev = self.events_list[step_idx]

            # Progress Bar
            percent = int((self.current_step / max(total_steps, 1)) * 100)
            progress_text = Text()
            progress_text.append(
                f"Progress: [{self.current_step}/{total_steps}] ", style="bold cyan"
            )
            progress_text.append(
                f"{'█' * (percent // 5)}{'░' * (20 - (percent // 5))} {percent}%\n",
                style="bold green",
            )

            state_str = "▶ PLAYING" if self.is_playing else "⏸ PAUSED"
            controls_text = Text()
            controls_text.append(
                f"State: {state_str} | Speed: {self.speed} | Controls: [Space] Play/Pause | [→] Step Next | [←] Step Prev\n",
                style="bold yellow",
            )

            event_info = Text()
            event_info.append(
                f"Step {ev['step']}: [{ev['type']}] at {ev['timestamp']}\n",
                style="bold cyan",
            )
            event_info.append(
                f"Source: {ev['source']} | Session: {ev['session']}\n\n", style="white"
            )
            event_info.append("Event Summary / Detail:\n", style="dim white")
            event_info.append(f"{ev['summary']}\n", style="bold green")

            main_panel = Panel(
                event_info,
                title="🎞️ Step-by-Step Event Replay Stream",
                border_style="cyan",
            )

            layout = Table.grid(expand=True)
            layout.add_row(
                Panel(
                    progress_text + controls_text,
                    title="🎮 Replay Controls",
                    border_style="green",
                )
            )
            layout.add_row(main_panel)
        else:
            empty_text = Text(
                "No recorded session events available for replay.\n", style="dim white"
            )
            layout = Panel(
                empty_text,
                title="🎞️ Step-by-Step Event Replay Stream",
                border_style="dim white",
            )

        return Panel(layout, title="[3] SESSION REPLAY ENGINE", border_style="green")
