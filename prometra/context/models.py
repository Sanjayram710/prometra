from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SessionSummary(BaseModel):
    session_id: str
    duration_seconds: int
    started_at: str
    warnings: List[str] = Field(default_factory=list)

class FileChange(BaseModel):
    path: str
    operation: str
    timestamp: str

class GitSnapshot(BaseModel):
    branch: str
    commit_id: Optional[str] = None
    changed_files: List[str] = Field(default_factory=list)

class TimelineSummary(BaseModel):
    total_events: int
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)

class AnalyzerSummary(BaseModel):
    health_score: float
    risk_level: str
    recommendation: str
    findings: List[str] = Field(default_factory=list)

class RepositorySummary(BaseModel):
    project_id: str
    root_path: str

class ProjectState(BaseModel):
    repo: RepositorySummary
    session: Optional[SessionSummary] = None
    git: Optional[GitSnapshot] = None
    recent_files: List[FileChange] = Field(default_factory=list)
    analyzer: Optional[AnalyzerSummary] = None

class Context(BaseModel):
    context_id: str
    generated_at: str
    project_state: ProjectState
    timeline: TimelineSummary
