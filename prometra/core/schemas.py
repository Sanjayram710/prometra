from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

def utcnow():
    return datetime.now(timezone.utc)

class Workspace(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    root_path: str
    repository: Optional[str] = None
    owner: Optional[str] = None
    client: Optional[str] = None
    environment: str = "development"
    framework: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    status: str = "active"
    configuration_version: str = "1.0"
    privacy_mode: str = "metadata_only"

class Session(BaseModel):
    session_id: str
    project_id: str
    start_ts: datetime = Field(default_factory=utcnow)
    end_ts: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    project_path: str
    working_directory: str
    git_repository: Optional[str] = None
    branch: Optional[str] = None
    starting_commit: Optional[str] = None
    ending_commit: Optional[str] = None
    connector: Optional[str] = None
    ai_tool: Optional[str] = None
    model: Optional[str] = None
    user: Optional[str] = None
    status: str = "active"
    event_counts: Dict[str, int] = Field(default_factory=dict)
    config_snapshot: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    confidence: float = 1.0

class FilesystemEvent(BaseModel):
    event_id: str
    session_id: str
    project_id: str
    timestamp: datetime = Field(default_factory=utcnow)
    path: str
    normalized_relative_path: str
    operation: str # created, modified, deleted, renamed
    old_path: Optional[str] = None
    new_path: Optional[str] = None
    size: int = 0
    language: Optional[str] = None
    file_hash: Optional[str] = None
    source: str = "filesystem"
    confidence: float = 1.0
    redaction_state: str = "unredacted"

class GitEvent(BaseModel):
    event_id: str
    repository: str
    branch: str
    commit_id: str
    parent_commits: List[str] = Field(default_factory=list)
    author: str
    committer: str
    message: str
    timestamp: datetime
    changed_files: List[str] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    diff_metadata: Dict[str, Any] = Field(default_factory=dict)
    merge_flag: bool = False
    tag: Optional[str] = None
    session_relation: Optional[str] = None
    source: str = "git"

class AIEvent(BaseModel):
    event_id: str
    session_id: str
    project_id: str
    connector: str
    ai_tool: str
    provider: str
    model: str
    model_version: Optional[str] = None
    prompt_id: Optional[str] = None
    prompt_version: Optional[str] = None
    prompt_content: Optional[str] = None
    response_content: Optional[str] = None
    token_counts: Dict[str, int] = Field(default_factory=dict)
    latency_ms: Optional[int] = None
    cost: Optional[float] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)
    consent_mode: str = "metadata_only"
    confidence: float = 1.0

class TimelineEvent(BaseModel):
    normalized_event_type: str
    timestamp: datetime
    sequence: int
    source: str
    actor_tool: Optional[str] = None
    session_id: Optional[str] = None
    related_event_ids: List[str] = Field(default_factory=list)
    summary: str
    details_access_level: str = "public"
    confidence: float = 1.0
    analysis_version: str = "1.0"
