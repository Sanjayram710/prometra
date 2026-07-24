import os
from typing import List, Optional, Dict, Any
from prometra.timemachine.models import CheckpointModel
from prometra.timemachine.storage import CheckpointStorage
from prometra.timemachine.snapshot import SnapshotEngine
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel

class CheckpointManager:
    """Atomic manager for creating, querying, listing, and persisting development checkpoints."""

    def __init__(self, storage: SQLiteStorage, root_dir: Optional[str] = None):
        self.storage = storage
        self.root_dir = root_dir or os.path.abspath(".")
        self.cp_storage = CheckpointStorage(root_dir=os.path.join(self.root_dir, ".prometra"))
        self.snapshot_engine = SnapshotEngine(storage=self.storage, root_dir=self.root_dir)

    def create_checkpoint(self, message: str = "Checkpoint", session_id: Optional[str] = None) -> CheckpointModel:
        """Create a new checkpoint atomically."""
        checkpoint, snapshots = self.snapshot_engine.capture_snapshot(message=message, session_id=session_id)
        self.cp_storage.save_checkpoint(checkpoint, snapshots)

        # Record checkpoint event in SQLite Timeline
        db = self.storage.get_session()
        try:
            tl = TimelineEventModel(
                normalized_event_type="checkpoint",
                timestamp=checkpoint.timestamp,
                sequence=999,
                source="timemachine",
                session_id=checkpoint.session_id,
                summary=f"Checkpoint: {checkpoint.message} ({checkpoint.id})"
            )
            db.add(tl)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()

        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointModel]:
        """Retrieve checkpoint metadata by ID."""
        return self.cp_storage.load_checkpoint(checkpoint_id)

    def list_checkpoints(self) -> List[CheckpointModel]:
        """List all saved checkpoints ordered chronologically."""
        return self.cp_storage.list_checkpoints()

    def search_checkpoints(self, query: str) -> List[CheckpointModel]:
        """Search checkpoints matching message, ID, or file paths."""
        query_lower = query.lower()
        all_cps = self.list_checkpoints()
        results: List[CheckpointModel] = []

        for cp in all_cps:
            if (
                query_lower in cp.id.lower()
                or query_lower in cp.message.lower()
                or query_lower in cp.summary.lower()
                or any(query_lower in f.lower() for f in cp.modified_files)
            ):
                results.append(cp)

        return results
