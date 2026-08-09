import datetime

from prometra.search.models import SearchFilter


class FilterValidator:
    """Validates and processes search filter inputs."""

    @staticmethod
    def parse_date(
        date_val: str | datetime.datetime | None,
    ) -> datetime.datetime | None:
        """Parse YYYY-MM-DD or ISO date string safely, returning datetime or None."""
        if not date_val:
            return None
        if isinstance(date_val, datetime.datetime):
            return date_val
        if isinstance(date_val, str):
            try:
                dt = datetime.datetime.fromisoformat(date_val)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=datetime.UTC)
                return dt
            except ValueError:
                # Invalid date string format
                return None
        return None

    @classmethod
    def process_filters(
        cls,
        query: str,
        category: str | None = None,
        session_id: str | None = None,
        since: str | datetime.datetime | None = None,
        until: str | datetime.datetime | None = None,
        today: bool = False,
        week: bool = False,
        limit: int | None = None,
        export: str | None = None,
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
            export=export,
        )
