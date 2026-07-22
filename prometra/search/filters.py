import datetime
from typing import Optional, Union, Dict, Any
from prometra.core.time import utcnow
from prometra.search.models import SearchFilter

class FilterValidator:
    """Validates and processes search filter inputs."""

    @staticmethod
    def parse_date(date_val: Optional[Union[str, datetime.datetime]]) -> Optional[datetime.datetime]:
        """Parse YYYY-MM-DD or ISO date string safely, returning datetime or None."""
        if not date_val:
            return None
        if isinstance(date_val, datetime.datetime):
            return date_val
        if isinstance(date_val, str):
            try:
                dt = datetime.datetime.fromisoformat(date_val)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt
            except ValueError:
                # Invalid date string format
                return None
        return None

    @classmethod
    def process_filters(
        cls,
        query: str,
        category: Optional[str] = None,
        session_id: Optional[str] = None,
        since: Optional[Union[str, datetime.datetime]] = None,
        until: Optional[Union[str, datetime.datetime]] = None,
        today: bool = False,
        week: bool = False,
        limit: Optional[int] = None,
        export: Optional[str] = None
    ) -> SearchFilter:
        """Process and validate raw search CLI parameters into a clean SearchFilter model."""
        since_dt = cls.parse_date(since)
        until_dt = cls.parse_date(until)

        return SearchFilter(
            query=query or "",
            category=category,
            session_id=session_id,
            since=since_dt,
            until=until_dt,
            today=today,
            week=week,
            limit=limit,
            export=export
        )
