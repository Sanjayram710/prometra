from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class SessionStats:
    """Detailed activity and productivity metrics for a single session."""
    session_id: str
    start_ts: Optional[str] = None
    duration_seconds: int = 0
    duration_minutes: int = 0
    files_created: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    git_commits: int = 0
    ai_events: int = 0
    total_events: int = 0
    productivity_metrics: Dict[str, Any] = field(default_factory=dict)
    event_type_distribution: Dict[str, int] = field(default_factory=dict)

@dataclass
class CompareResult:
    """Comparison results and metric differences between two sessions."""
    session_a: str
    session_b: str
    stats_a: SessionStats
    stats_b: SessionStats
    duration_difference: str
    duration_seconds_difference: int
    files_created_difference: int
    files_modified_difference: int
    files_deleted_difference: int
    git_commit_difference: int
    ai_event_difference: int
    total_events_difference: int
    timeline_difference: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompareOptions:
    """Options for session comparison execution."""
    session_a: Optional[str] = None
    session_b: Optional[str] = None
    latest: bool = False
    json_output: bool = False
    markdown_output: bool = False
    export_path: Optional[str] = None
