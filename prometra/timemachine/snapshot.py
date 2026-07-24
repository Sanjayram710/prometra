import os
import uuid
import datetime
from typing import List, Dict, Any, Tuple, Optional

from prometra.timemachine.models import FileSnapshot, CheckpointModel
from prometra.timemachine.storage import CheckpointStorage
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, SessionModel
from prometra.intelligence.analyzer import IntelligenceAnalyzer
from prometra.tracker.ignore import IgnoreManager
from prometra.core.time import utcnow

class SnapshotEngine:
    """Captures current project file snapshots, Git state, AI prompts, and productivity metrics."""

    def __init__(self, storage: SQLiteStorage, root_dir: Optional[str] = None):
        self.storage = storage
        self.root_dir = root_dir or os.path.abspath(".")
        self.ignore = IgnoreManager(self.root_dir)

    def _get_git_info(self) -> Tuple[str, str]:
        """Extract current Git branch and commit hash if available."""
        try:
            from git import Repo
            repo = Repo(self.root_dir, search_parent_directories=True)
            branch = repo.active_branch.name if not repo.head.is_detached else "detached"
            commit = repo.head.commit.hexsha[:7]
            return branch, commit
        except Exception:
            return "main", "N/A"

    def capture_snapshot(self, message: str = "Checkpoint", session_id: Optional[str] = None) -> Tuple[CheckpointModel, List[FileSnapshot]]:
        """Capture full project snapshot and build CheckpointModel."""
        now = utcnow()
        branch, commit = self._get_git_info()

        # 1. Analyze session intelligence for productivity score
        intelligence_score = 0
        ai_prompts_count = 0
        summary_text = message

        try:
            analyzer = IntelligenceAnalyzer(self.storage)
            intel_res = analyzer.analyze_session(session_id=session_id)
            intelligence_score = intel_res.productivity.score
            ai_prompts_count = intel_res.ai_usage.total_prompts
            if not message or message == "Checkpoint":
                summary_text = f"{intel_res.classification.primary_category}: {intel_res.summary.total_events} events"
        except Exception:
            pass

        # 2. Scan workspace files
        snapshots: List[FileSnapshot] = []
        file_hashes: Dict[str, str] = {}
        modified_files: List[str] = []

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

                    h = CheckpointStorage.compute_file_hash(content)
                    file_hashes[rel_path] = h
                    modified_files.append(rel_path)

                    snapshots.append(FileSnapshot(
                        path=abs_path,
                        normalized_path=rel_path,
                        file_hash=h,
                        size=len(content),
                        content=content
                    ))
                except Exception:
                    pass

        # 3. Create Checkpoint object
        cp_id = f"chk-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        sess_id = session_id or "sess-active"

        checkpoint = CheckpointModel(
            id=cp_id,
            message=message,
            timestamp=now,
            session_id=sess_id,
            project_id="default",
            git_branch=branch,
            git_commit=commit,
            modified_files=modified_files,
            file_hashes=file_hashes,
            ai_prompts=ai_prompts_count,
            productivity_score=intelligence_score,
            summary=summary_text
        )

        return checkpoint, snapshots
