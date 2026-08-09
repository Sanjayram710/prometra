import contextlib
import datetime
import time
from typing import Any, ClassVar

from prometra.replay.renderer import ReplayRenderer
from prometra.storage.models import TimelineEventModel


class ReplayPlayer:
    """Plays back session events with speed acceleration or step-by-step control."""

    SPEED_FACTORS: ClassVar[dict[str, float]] = {"1x": 1.0, "2x": 2.0, "5x": 5.0, "10x": 10.0, "instant": 0.0}

    def __init__(self, renderer: ReplayRenderer | None = None):
        self.renderer = renderer or ReplayRenderer()

    def play(
        self,
        events: list[TimelineEventModel],
        session_info: dict[str, Any],
        speed: str = "instant",
        step: bool = False,
        interactive_input: bool = True,
    ):
        """Execute playback loop over timeline events."""
        self.renderer.render_session_header(session_info)

        speed_lower = (speed or "instant").lower()
        factor = self.SPEED_FACTORS.get(speed_lower, 0.0)

        total_events = len(events)
        last_ts: datetime.datetime | None = None

        for idx, e in enumerate(events, start=1):
            if step and idx > 1 and interactive_input:
                with contextlib.suppress(EOFError, KeyboardInterrupt):
                    input("  [Press Enter to step to next event...]")

            elif factor > 0.0 and last_ts and e.timestamp:
                with contextlib.suppress(Exception):
                    if (
                        factor > 0
                        and isinstance(e.timestamp, datetime.datetime)
                        and isinstance(last_ts, datetime.datetime)
                    ):
                        delta = (e.timestamp - last_ts).total_seconds()
                        if delta > 0:
                            sleep_time = min(delta / factor, 2.0)
                            time.sleep(sleep_time)

            last_ts = (
                e.timestamp if isinstance(e.timestamp, datetime.datetime) else None
            )
            self.renderer.render_event(e, step_number=idx, total_steps=total_events)

        self.renderer.render_footer(session_info)
