import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class SearchFilter(BaseModel):
    """Criteria and options for executing search queries."""
    query: str
    category: Optional[str] = None
    session_id: Optional[str] = None
    since: Optional[datetime.datetime] = None
    until: Optional[datetime.datetime] = None
    today: bool = False
    week: bool = False
    limit: Optional[int] = None
    export: Optional[str] = None

class SearchResultItem(BaseModel):
    """Individual search result item representing a matched event."""
    event_id: Union[str, int]
    timestamp: Optional[datetime.datetime] = None
    category: str = "Event"
    source: str = "system"
    actor_tool: Optional[str] = None
    session_id: Optional[str] = None
    summary: str = ""
    matched_field: str = "summary"

class SearchResultSet(BaseModel):
    """Container for search execution results, metrics, and metadata."""
    query: str
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    total_results: int = 0
    execution_time_ms: float = 0.0
    results: List[SearchResultItem] = Field(default_factory=list)
