import time
import datetime
from typing import List, Dict, Any, Optional
from prometra.storage.models import TimelineEventModel
from prometra.replay.renderer import ReplayRenderer

class ReplayPlayer:
    """Plays back session events with speed acceleration or step-by-step control."""

    SPEED_FACTORS = {
        "1x": 1.0,
        "2x": 2.0,
        "5x": 5.0,
        "10x": 10.0,
        "instant": 0.0
    }

    def __init__(self, renderer: Optional[ReplayRenderer] = None):
        self.renderer = renderer or ReplayRenderer()

    def play(
        self,
        events: List[TimelineEventModel],
        session_info: Dict[str, Any],
        speed: str = "instant",
        step: bool = False,
        interactive_input: bool = True
    ):
        """Execute playback loop over timeline events."""
        self.renderer.render_session_header(session_info)

        speed_lower = (speed or "instant").lower()
        factor = self.SPEED_FACTORS.get(speed_lower, 0.0)

        total_events = len(events)
        last_ts: Optional[datetime.datetime] = None

        for idx, e in enumerate(events, start=1):
            if step and idx > 1 and interactive_input:
                try:
                    input("  [Press Enter to step to next event...]")
                except (EOFError, KeyboardInterrupt):
                    break

            elif factor > 0.0 and last_ts and e.timestamp:
                try:
                    # Calculate real timestamp delta
                    if isinstance(e.timestamp, datetime.datetime) and isinstance(last_ts, datetime.datetime):
                        delta = (e.timestamp - last_ts).total_seconds()
                        if delta > 0:
                            sleep_time = min(delta / factor, 2.0) # Cap sleep at 2 seconds max
                            time.sleep(sleep_time)
                except Exception:
                    pass

            last_ts = e.timestamp if isinstance(e.timestamp, datetime.datetime) else None
            self.renderer.render_event(e, step_number=idx, total_steps=total_events)

        self.renderer.render_footer(session_info)
