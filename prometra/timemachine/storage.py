import hashlib
import json
import os

from prometra.timemachine.models import CheckpointModel, FileSnapshot


class CheckpointStorage:
    """Manages local disk storage for checkpoints and file snapshots inside .prometra/checkpoints/."""

    def __init__(self, root_dir: str | None = None):
        self.root_dir = root_dir or os.path.abspath(".prometra")
        self.checkpoints_dir = os.path.join(self.root_dir, "checkpoints")
        os.makedirs(self.checkpoints_dir, exist_ok=True)

    @staticmethod
    def compute_file_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()

    def save_checkpoint(
        self, checkpoint: CheckpointModel, snapshots: list[FileSnapshot]
    ) -> str:
        """Save a checkpoint and its file snapshots to local storage."""
        cp_dir = os.path.join(self.checkpoints_dir, checkpoint.id)
        os.makedirs(cp_dir, exist_ok=True)

        # 1. Save files contents
        files_dir = os.path.join(cp_dir, "files")
        os.makedirs(files_dir, exist_ok=True)

        for s in snapshots:
            if s.content is not None and not s.is_deleted:
                rel_safe = s.normalized_path.replace(":", "_").replace("\\", "/")
                file_dest = os.path.join(files_dir, rel_safe)
                os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                with open(file_dest, "w", encoding="utf-8", errors="replace") as f:
                    f.write(s.content)

        # 2. Save metadata JSON
        meta_path = os.path.join(cp_dir, "metadata.json")
        cp_dict = checkpoint.model_dump(mode="json")
        cp_dict["snapshot_path"] = cp_dir

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(cp_dict, f, indent=2)

        return cp_dir

    def load_checkpoint(self, checkpoint_id: str) -> CheckpointModel | None:
        """Load checkpoint metadata from storage."""
        cp_dir = os.path.join(self.checkpoints_dir, checkpoint_id)
        meta_path = os.path.join(cp_dir, "metadata.json")
        if not os.path.exists(meta_path):
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CheckpointModel(**data)
        except (OSError, ValueError, TypeError):
            return None

    def load_file_content(
        self, checkpoint_id: str, relative_path: str
    ) -> str | None:
        """Load specific file content from a checkpoint snapshot."""
        rel_safe = relative_path.replace(":", "_").replace("\\", "/")
        file_path = os.path.join(self.checkpoints_dir, checkpoint_id, "files", rel_safe)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()
            except OSError:
                return None
        return None

    def list_checkpoints(self) -> list[CheckpointModel]:
        """List all checkpoints sorted chronologically."""
        results: list[CheckpointModel] = []
        if not os.path.exists(self.checkpoints_dir):
            return results

        for entry in os.listdir(self.checkpoints_dir):
            cp = self.load_checkpoint(entry)
            if cp:
                results.append(cp)

        results.sort(key=lambda c: c.timestamp, reverse=True)
        return results
