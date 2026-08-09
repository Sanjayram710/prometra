import json
from typing import Any

from prometra.storage.models import TimelineEventModel


class ReplayFormatter:
    """Formats session replay data for JSON and Markdown representations."""

    @staticmethod
    def get_event_icon(event_type: str) -> str:
        net = (event_type or "").lower()
        if "sessionstart" in net:
            return "[START]"
        elif "sessionend" in net or "sessionstop" in net:
            return "[END]"
        elif "prompt" in net:
            return "[PROMPT]"
        elif "response" in net:
            return "[AI]"
        elif "tool" in net:
            return "[TOOL]"
        elif "filesystem" in net or "file" in net:
            return "[FILE]"
        elif "git" in net:
            return "[GIT]"
        elif "error" in net or "fail" in net:
            return "[ERR]"
        return "[*]"

    @classmethod
    def to_json(
        cls, session_info: dict[str, Any], events: list[TimelineEventModel]
    ) -> str:
        event_list = []
        for e in events:
            event_list.append(
                {
                    "id": e.id,
                    "timestamp": str(e.timestamp) if e.timestamp else "",
                    "event_type": e.normalized_event_type or "",
                    "source": e.source or "",
                    "summary": e.summary or "",
                    "sequence": e.sequence,
                }
            )
        data = {"session_info": session_info, "events": event_list}
        return json.dumps(data, indent=2)

    @classmethod
    def to_markdown(
        cls, session_info: dict[str, Any], events: list[TimelineEventModel]
    ) -> str:
        dur = session_info.get("duration_seconds", 0)
        dur_str = f"{dur // 60}m {dur % 60}s" if dur >= 60 else f"{dur}s"

        lines = [
            f"# Prometra Session Replay: {session_info.get('session_id', '')}\n",
            f"- **Start Time:** `{session_info.get('start_ts', '')}`",
            f"- **Duration:** `{dur_str}`",
            f"- **Total Events:** `{session_info.get('total_events', len(events))}`",
            f"- **Status:** `{session_info.get('status', 'completed')}`\n",
            "---",
            "\n### Replay Timeline\n",
        ]

        for e in events:
            icon = cls.get_event_icon(e.normalized_event_type)
            ts = (
                str(e.timestamp).split(" ")[-1][:8]
                if e.timestamp and " " in str(e.timestamp)
                else str(e.timestamp)
            )
            net = e.normalized_event_type or "Event"
            src = e.source or "system"
            summary = e.summary or ""
            lines.append(f"- **{ts}** {icon} **{net}** (`{src}`): {summary}")

        return "\n".join(lines)
