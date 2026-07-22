from typing import Dict, Any, List
from pydantic import BaseModel, Field
from prometra.timeline.queries import TimelineQueryEngine
from prometra.timeline.filters import TimelineFilter

class SummaryMetrics(BaseModel):
    """Container for timeline summary metrics."""
    sessions_count: int = 0
    files_modified: int = 0
    git_commits: int = 0
    ai_events: int = 0
    connectors_used: List[str] = Field(default_factory=list)
    total_events: int = 0

class TimelineSummaryGenerator:
    """Generates summary statistics for Prometra timelines."""

    def __init__(self, query_engine: TimelineQueryEngine):
        self.query_engine = query_engine

    def generate(self, filters: TimelineFilter) -> SummaryMetrics:
        raw_data = self.query_engine.fetch_summary(filters)
        return SummaryMetrics(
            sessions_count=raw_data.get("sessions_count", 0),
            files_modified=raw_data.get("files_modified", 0),
            git_commits=raw_data.get("git_commits", 0),
            ai_events=raw_data.get("ai_events", 0),
            connectors_used=raw_data.get("connectors_used", []),
            total_events=raw_data.get("total_events", 0)
        )
