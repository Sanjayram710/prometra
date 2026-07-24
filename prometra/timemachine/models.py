from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class FileSnapshot(BaseModel):
    path: str
    normalized_path: str
    file_hash: str
    size: int
    content: Optional[str] = None
    is_deleted: bool = False

class CheckpointModel(BaseModel):
    id: str
    message: str
    timestamp: datetime
    session_id: str
    project_id: str = "default"
    git_branch: str = "main"
    git_commit: str = "N/A"
    modified_files: List[str] = Field(default_factory=list)
    file_hashes: Dict[str, str] = Field(default_factory=dict)
    ai_prompts: int = 0
    ai_responses_metadata: List[Dict[str, Any]] = Field(default_factory=list)
    productivity_score: int = 0
    summary: str = ""
    snapshot_path: Optional[str] = None

class RestorePreview(BaseModel):
    checkpoint_id: str
    files_created: List[str] = Field(default_factory=list)
    files_modified: List[str] = Field(default_factory=list)
    files_deleted: List[str] = Field(default_factory=list)
    unchanged_files: List[str] = Field(default_factory=list)

class CheckpointDiff(BaseModel):
    checkpoint_a: str
    checkpoint_b: str
    added_files: List[str] = Field(default_factory=list)
    removed_files: List[str] = Field(default_factory=list)
    modified_files: List[str] = Field(default_factory=list)
    diff_text: str = ""
