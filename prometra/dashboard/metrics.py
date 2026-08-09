from pydantic import BaseModel, Field


class TopFileEntry(BaseModel):
    path: str
    edits: int


class TopModelEntry(BaseModel):
    model_name: str
    count: int


class SessionMetrics(BaseModel):
    total_sessions: int = 0
    total_duration_seconds: int = 0
    longest_session_seconds: int = 0
    avg_session_length_seconds: int = 0


class FilesystemMetrics(BaseModel):
    files_created: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    top_edited_files: list[TopFileEntry] = Field(default_factory=list)


class GitMetrics(BaseModel):
    total_commits: int = 0
    commits_per_day: float = 0.0


class AiMetrics(BaseModel):
    ai_prompts: int = 0
    ai_responses: int = 0
    tool_calls: int = 0
    errors: int = 0
    retries: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    avg_response_time_ms: float = 0.0
    top_models: list[TopModelEntry] = Field(default_factory=list)
    connectors_used: list[str] = Field(default_factory=list)


class ActivityMetrics(BaseModel):
    top_active_hours: list[int] = Field(default_factory=list)
    daily_activity: dict[str, int] = Field(default_factory=dict)


class DashboardMetrics(BaseModel):
    filter_label: str = "All Time"
    sessions: SessionMetrics = Field(default_factory=SessionMetrics)
    filesystem: FilesystemMetrics = Field(default_factory=FilesystemMetrics)
    git: GitMetrics = Field(default_factory=GitMetrics)
    ai: AiMetrics = Field(default_factory=AiMetrics)
    activity: ActivityMetrics = Field(default_factory=ActivityMetrics)
