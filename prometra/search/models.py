import datetime
from typing import Any

from pydantic import BaseModel, Field


class SearchFilter(BaseModel):
    """Criteria and options for executing search queries."""

    query: str
    category: str | None = None
    session_id: str | None = None
    since: datetime.datetime | None = None
    until: datetime.datetime | None = None
    today: bool = False
    week: bool = False
    limit: int | None = None
    export: str | None = None


class SearchResultItem(BaseModel):
    """Individual search result item representing a matched event."""

    event_id: str | int
    timestamp: datetime.datetime | None = None
    category: str = "Event"
    source: str = "system"
    actor_tool: str | None = None
    session_id: str | None = None
    summary: str = ""
    matched_field: str = "summary"


class SearchResultSet(BaseModel):
    """Container for search execution results, metrics, and metadata."""

    query: str
    applied_filters: dict[str, Any] = Field(default_factory=dict)
    total_results: int = 0
    execution_time_ms: float = 0.0
    results: list[SearchResultItem] = Field(default_factory=list)
