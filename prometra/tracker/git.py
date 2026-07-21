import git
import threading
import time
from typing import Optional
from datetime import datetime, timezone
from prometra.core.time import utcnow

class GitTracker:
    def __init__(self, repo_path: str, timeline_engine, session_id: str):
        self.repo_path = repo_path
        self.timeline_engine = timeline_engine
        self.session_id = session_id
        self.running = False
        self.thread = None
        self.last_commit_scanned = None
        
        try:
            self.repo = git.Repo(self.repo_path)
            try:
                self.last_commit_scanned = self.repo.head.commit.hexsha
            except ValueError:
                pass
        except git.InvalidGitRepositoryError:
            self.repo = None

    def start(self):
        if not self.repo:
            return
        self.running = True
        self.thread = threading.Thread(target=self._poll_commits)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _poll_commits(self):
        while self.running:
            time.sleep(2)
            try:
                current_head = self.repo.head.commit.hexsha
                if current_head != self.last_commit_scanned:
                    # New commit detected
                    self._process_commit(current_head)
                    self.last_commit_scanned = current_head
            except Exception:
                pass

    def _process_commit(self, commit_hash: str):
        commit = self.repo.commit(commit_hash)
        
        insertions = 0
        deletions = 0
        changed_files = []
        is_merge = len(commit.parents) > 1
        parent_commits = [p.hexsha for p in commit.parents]
        
        tags = [tag.name for tag in self.repo.tags if tag.commit.hexsha == commit.hexsha]
        tag_str = tags[0] if tags else None
        
        if commit.parents:
            parent = commit.parents[0]
            diffs = parent.diff(commit, create_patch=True)
            for d in diffs:
                diff_text = d.diff.decode('utf-8', errors='replace')
                for line in diff_text.splitlines():
                    if line.startswith('+') and not line.startswith('+++'):
                        insertions += 1
                    elif line.startswith('-') and not line.startswith('---'):
                        deletions += 1
                if d.a_path: changed_files.append(d.a_path)
                if d.b_path and d.b_path not in changed_files: changed_files.append(d.b_path)
        else:
            changed_files = list(commit.stats.files.keys())
            insertions = commit.stats.total['insertions']
            deletions = commit.stats.total['deletions']

        event_info = {
            "type": "git",
            "session_id": self.session_id,
            "timestamp": datetime.fromtimestamp(commit.committed_date, timezone.utc),
            "repository": self.repo_path,
            "branch": self.get_current_branch() or "detached",
            "commit_id": commit.hexsha,
            "parent_commits": parent_commits,
            "author": f"{commit.author.name} <{commit.author.email}>",
            "message": commit.message,
            "insertions": insertions,
            "deletions": deletions,
            "changed_files": list(set(changed_files)),
            "merge_flag": is_merge,
            "tag": tag_str,
            "source": "git",
            "summary": f"Git commit {commit.hexsha[:7]}: {commit.summary}"
        }
        self.timeline_engine.append_event(event_info)

    def get_current_branch(self) -> Optional[str]:
        if not self.repo:
            return None
        try:
            return self.repo.active_branch.name
        except TypeError:
            return "detached"
