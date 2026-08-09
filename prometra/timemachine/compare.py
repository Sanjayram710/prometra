import difflib
import os

from prometra.timemachine.models import CheckpointDiff
from prometra.timemachine.storage import CheckpointStorage


class CheckpointComparer:
    """Computes file diffs and metrics comparisons between any two checkpoints."""

    def __init__(self, root_dir: str | None = None):
        self.root_dir = root_dir or os.path.abspath(".")
        self.cp_storage = CheckpointStorage(
            root_dir=os.path.join(self.root_dir, ".prometra")
        )

    def compare_checkpoints(
        self, checkpoint_a: str, checkpoint_b: str
    ) -> CheckpointDiff:
        """Compare two checkpoints and return added, removed, modified files, and unified diff."""
        cp1 = self.cp_storage.load_checkpoint(checkpoint_a)
        cp2 = self.cp_storage.load_checkpoint(checkpoint_b)

        if not cp1:
            raise ValueError(f"Checkpoint '{checkpoint_a}' not found.")
        if not cp2:
            raise ValueError(f"Checkpoint '{checkpoint_b}' not found.")

        hashes1 = cp1.file_hashes or {}
        hashes2 = cp2.file_hashes or {}

        added_files: list[str] = []
        removed_files: list[str] = []
        modified_files: list[str] = []

        all_paths = set(hashes1.keys()).union(set(hashes2.keys()))

        diff_chunks: list[str] = []

        for path in sorted(all_paths):
            in1 = path in hashes1
            in2 = path in hashes2

            if not in1 and in2:
                added_files.append(path)
            elif in1 and not in2:
                removed_files.append(path)
            elif hashes1.get(path) != hashes2.get(path):
                modified_files.append(path)

            if hashes1.get(path) != hashes2.get(path):
                c1 = self.cp_storage.load_file_content(cp1.id, path) or ""
                c2 = self.cp_storage.load_file_content(cp2.id, path) or ""

                lines1 = c1.splitlines(keepends=True)
                lines2 = c2.splitlines(keepends=True)

                u_diff = list(
                    difflib.unified_diff(
                        lines1,
                        lines2,
                        fromfile=f"a/{path} ({cp1.id})",
                        tofile=f"b/{path} ({cp2.id})",
                    )
                )
                if u_diff:
                    diff_chunks.extend(u_diff)

        diff_text = "".join(diff_chunks)

        return CheckpointDiff(
            checkpoint_a=cp1.id,
            checkpoint_b=cp2.id,
            added_files=added_files,
            removed_files=removed_files,
            modified_files=modified_files,
            diff_text=diff_text,
        )
