import os
from typing import Any

from prometra.replay.formatter import ReplayFormatter
from prometra.storage.models import TimelineEventModel


class ReplayExporter:
    """Exports session replay data to file paths (.md, .json)."""

    @classmethod
    def export(
        cls,
        session_info: dict[str, Any],
        events: list[TimelineEventModel],
        export_path: str,
    ) -> str:
        ext = os.path.splitext(export_path)[1].lower()
        if ext == ".json":
            content = ReplayFormatter.to_json(session_info, events)
        elif ext == ".md" or ext == ".markdown":
            content = ReplayFormatter.to_markdown(session_info, events)
        else:
            content = ReplayFormatter.to_markdown(session_info, events)

        parent_dir = os.path.dirname(export_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)

        return export_path
