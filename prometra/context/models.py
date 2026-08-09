from typing import Any

from pydantic import BaseModel, Field


class SessionSummary(BaseModel):
    session_id: str
    duration_seconds: int
    started_at: str
    warnings: list[str] = Field(default_factory=list)


class FileChange(BaseModel):
    path: str
    operation: str
    timestamp: str


class GitSnapshot(BaseModel):
    branch: str
    commit_id: str | None = None
    changed_files: list[str] = Field(default_factory=list)


class TimelineSummary(BaseModel):
    total_events: int
    recent_events: list[dict[str, Any]] = Field(default_factory=list)


class AnalyzerSummary(BaseModel):
    health_score: float
    risk_level: str
    recommendation: str
    findings: list[str] = Field(default_factory=list)


class RepositorySummary(BaseModel):
    project_id: str
    root_path: str


class ProjectState(BaseModel):
    repo: RepositorySummary
    session: SessionSummary | None = None
    git: GitSnapshot | None = None
    recent_files: list[FileChange] = Field(default_factory=list)
    analyzer: AnalyzerSummary | None = None


class Context(BaseModel):
    context_id: str
    generated_at: str
    project_state: ProjectState
    timeline: TimelineSummary
