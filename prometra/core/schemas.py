from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from prometra.core.time import utcnow


class Workspace(BaseModel):
    project_id: str
    name: str
    description: str | None = None
    root_path: str
    repository: str | None = None
    owner: str | None = None
    client: str | None = None
    environment: str = "development"
    framework: str | None = None
    languages: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    status: str = "active"
    configuration_version: str = "1.0"
    privacy_mode: str = "metadata_only"


class Session(BaseModel):
    session_id: str
    project_id: str
    start_ts: datetime = Field(default_factory=utcnow)
    end_ts: datetime | None = None
    duration_seconds: int | None = None
    project_path: str
    working_directory: str
    git_repository: str | None = None
    branch: str | None = None
    starting_commit: str | None = None
    ending_commit: str | None = None
    connector: str | None = None
    ai_tool: str | None = None
    model: str | None = None
    user: str | None = None
    status: str = "active"
    event_counts: dict[str, int] = Field(default_factory=dict)
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class FilesystemEvent(BaseModel):
    event_id: str
    session_id: str
    project_id: str
    timestamp: datetime = Field(default_factory=utcnow)
    path: str
    normalized_relative_path: str
    operation: str  # created, modified, deleted, renamed
    old_path: str | None = None
    new_path: str | None = None
    size: int = 0
    language: str | None = None
    file_hash: str | None = None
    source: str = "filesystem"
    confidence: float = 1.0
    redaction_state: str = "unredacted"


class GitEvent(BaseModel):
    event_id: str
    repository: str
    branch: str
    commit_id: str
    parent_commits: list[str] = Field(default_factory=list)
    author: str
    committer: str
    message: str
    timestamp: datetime
    changed_files: list[str] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    diff_metadata: dict[str, Any] = Field(default_factory=dict)
    merge_flag: bool = False
    tag: str | None = None
    session_relation: str | None = None
    source: str = "git"


class AIEvent(BaseModel):
    event_id: str
    session_id: str
    project_id: str
    connector: str
    ai_tool: str
    provider: str
    model: str
    model_version: str | None = None
    prompt_id: str | None = None
    prompt_version: str | None = None
    prompt_content: str | None = None
    response_content: str | None = None
    token_counts: dict[str, int] = Field(default_factory=dict)
    latency_ms: int | None = None
    cost: float | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    conversation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)
    consent_mode: str = "metadata_only"
    confidence: float = 1.0


class TimelineEvent(BaseModel):
    normalized_event_type: str
    timestamp: datetime
    sequence: int
    source: str
    actor_tool: str | None = None
    session_id: str | None = None
    related_event_ids: list[str] = Field(default_factory=list)
    summary: str
    details_access_level: str = "public"
    confidence: float = 1.0
    analysis_version: str = "1.0"
