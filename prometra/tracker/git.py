import git
from typing import Optional

class GitTracker:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = None

    def get_current_branch(self) -> Optional[str]:
        if not self.repo:
            return None
        try:
            return self.repo.active_branch.name
        except TypeError:
            return "detached"

    def get_head_commit(self) -> Optional[str]:
        if not self.repo:
            return None
        try:
            return self.repo.head.commit.hexsha
        except ValueError:
            return None
