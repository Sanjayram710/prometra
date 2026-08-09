from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FileSnapshot(BaseModel):
    path: str
    normalized_path: str
    file_hash: str
    size: int
    content: str | None = None
    is_deleted: bool = False


class CheckpointModel(BaseModel):
    id: str
    message: str
    timestamp: datetime
    session_id: str
    project_id: str = "default"
    git_branch: str = "main"
    git_commit: str = "N/A"
    modified_files: list[str] = Field(default_factory=list)
    file_hashes: dict[str, str] = Field(default_factory=dict)
    ai_prompts: int = 0
    ai_responses_metadata: list[dict[str, Any]] = Field(default_factory=list)
    productivity_score: int = 0
    summary: str = ""
    snapshot_path: str | None = None


class RestorePreview(BaseModel):
    checkpoint_id: str
    files_created: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    files_deleted: list[str] = Field(default_factory=list)
    unchanged_files: list[str] = Field(default_factory=list)


class CheckpointDiff(BaseModel):
    checkpoint_a: str
    checkpoint_b: str
    added_files: list[str] = Field(default_factory=list)
    removed_files: list[str] = Field(default_factory=list)
    modified_files: list[str] = Field(default_factory=list)
    diff_text: str = ""
