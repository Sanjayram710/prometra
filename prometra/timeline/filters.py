
from pydantic import BaseModel


class TimelineFilter(BaseModel):
    """Filter criteria for Timeline queries."""

    session_id: str | None = None
    event_type: str | None = None
    connector: str | None = None
    search: str | None = None
    today: bool = False
    limit: int | None = None
    offset: int = 0
    reverse: bool = False
    group: str | None = None
    summary: bool = False
    export: str | None = None
