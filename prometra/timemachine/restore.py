import os
import shutil
from typing import Optional, List, Dict, Any, Tuple

from prometra.timemachine.models import RestorePreview, CheckpointModel
from prometra.timemachine.storage import CheckpointStorage
from prometra.tracker.ignore import IgnoreManager

class RestoreEngine:
    """Provides pre-restore preview of affected files and safe restoration of project state."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = root_dir or os.path.abspath(".")
        self.cp_storage = CheckpointStorage(root_dir=os.path.join(self.root_dir, ".prometra"))
        self.ignore = IgnoreManager(self.root_dir)

    def preview_restore(self, checkpoint_id: str) -> RestorePreview:
        """Compute differences between target checkpoint and current workspace."""
        checkpoint = self.cp_storage.load_checkpoint(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint '{checkpoint_id}' not found.")

        target_hashes = checkpoint.file_hashes or {}

        # Scan current workspace files
        current_hashes: Dict[str, str] = {}
        for root, _, files in os.walk(self.root_dir):
            if ".prometra" in root or ".git" in root or "venv" in root or "__pycache__" in root:
                continue

            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, self.root_dir).replace("\\", "/")

                if self.ignore.should_ignore(rel_path):
                    continue

                try:
                    with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    current_hashes[rel_path] = CheckpointStorage.compute_file_hash(content)
                except Exception:
                    pass

        files_created: List[str] = []
        files_modified: List[str] = []
        files_deleted: List[str] = []
        unchanged_files: List[str] = []

        all_paths = set(target_hashes.keys()).union(set(current_hashes.keys()))

        for path in sorted(list(all_paths)):
            in_target = path in target_hashes
            in_current = path in current_hashes

            if in_target and not in_current:
                files_created.append(path)
            elif not in_target and in_current:
                files_deleted.append(path)
            elif target_hashes.get(path) != current_hashes.get(path):
                files_modified.append(path)
            else:
                unchanged_files.append(path)

        return RestorePreview(
            checkpoint_id=checkpoint_id,
            files_created=files_created,
            files_modified=files_modified,
            files_deleted=files_deleted,
            unchanged_files=unchanged_files
        )

    def execute_restore(self, checkpoint_id: str) -> bool:
        """Restore project state from target checkpoint."""
        preview = self.preview_restore(checkpoint_id)

        # 1. Restore created and modified files
        for rel_path in preview.files_created + preview.files_modified:
            content = self.cp_storage.load_file_content(checkpoint_id, rel_path)
            if content is not None:
                abs_dest = os.path.join(self.root_dir, rel_path)
                os.makedirs(os.path.dirname(abs_dest), exist_ok=True)
                with open(abs_dest, "w", encoding="utf-8", errors="replace") as f:
                    f.write(content)

        # 2. Remove deleted files
        for rel_path in preview.files_deleted:
            abs_dest = os.path.join(self.root_dir, rel_path)
            if os.path.exists(abs_dest) and os.path.isfile(abs_dest):
                try:
                    os.remove(abs_dest)
                except Exception:
                    pass

        return True
