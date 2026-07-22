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
    ai_prompts: int = 0
    ai_responses: int = 0
    tool_calls: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
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
            ai_prompts=raw_data.get("ai_prompts", 0),
            ai_responses=raw_data.get("ai_responses", 0),
            tool_calls=raw_data.get("tool_calls", 0),
            total_tokens=raw_data.get("total_tokens", 0),
            input_tokens=raw_data.get("input_tokens", 0),
            output_tokens=raw_data.get("output_tokens", 0),
            estimated_cost=raw_data.get("estimated_cost", 0.0),
            connectors_used=raw_data.get("connectors_used", []),
            total_events=raw_data.get("total_events", 0)
        )
