import os
from typing import Any

from prometra.core.time import utcnow
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter
from prometra.timemachine.checkpoint import CheckpointManager


class CheckpointTimeline:
    """Merges checkpoint markers into timeline event listings."""

    def __init__(self, storage: SQLiteStorage, root_dir: str | None = None):
        self.storage = storage
        self.root_dir = root_dir or os.path.abspath(".")
        self.cp_manager = CheckpointManager(
            storage=self.storage, root_dir=self.root_dir
        )

    def get_timeline_with_checkpoints(
        self, session_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve combined timeline events and checkpoint markers chronologically."""
        engine = TimelineEngine(self.storage)
        filters = TimelineFilter(session_id=session_id, limit=50)
        events_res = engine.query_events(filters=filters)

        combined: list[dict[str, Any]] = []

        for e in events_res:
            combined.append(
                {
                    "type": "event",
                    "id": str(e.id),
                    "event_type": e.normalized_event_type,
                    "timestamp": e.timestamp,
                    "summary": e.summary or "",
                    "session_id": e.session_id or "",
                }
            )

        # Add checkpoints
        checkpoints = self.cp_manager.list_checkpoints()
        for cp in checkpoints:
            if not session_id or cp.session_id == session_id:
                combined.append(
                    {
                        "type": "checkpoint",
                        "id": cp.id,
                        "event_type": "checkpoint",
                        "timestamp": cp.timestamp,
                        "summary": f"📍 Checkpoint [{cp.id}]: {cp.message} ({len(cp.modified_files)} files)",
                        "session_id": cp.session_id,
                    }
                )

        combined.sort(
            key=lambda x: x["timestamp"] if x["timestamp"] else utcnow(), reverse=True
        )
        return combined
