from typing import Optional
from pydantic import BaseModel, Field

class TimelineFilter(BaseModel):
    """Filter criteria for Timeline queries."""
    session_id: Optional[str] = None
    event_type: Optional[str] = None
    connector: Optional[str] = None
    search: Optional[str] = None
    today: bool = False
    limit: Optional[int] = None
    offset: int = 0
    reverse: bool = False
    group: Optional[str] = None
    summary: bool = False
    export: Optional[str] = None
