import datetime
import time

from prometra.search.filters import FilterValidator
from prometra.search.models import SearchResultItem, SearchResultSet
from prometra.search.query_builder import SearchQueryBuilder
from prometra.storage.sqlite import SQLiteStorage


class SearchEngine:
    """Core search engine for executing query searches and measuring performance."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.query_builder = SearchQueryBuilder()

    def search_events(
        self,
        query: str,
        category: str | None = None,
        session: str | None = None,
        since: str | datetime.datetime | None = None,
        until: str | datetime.datetime | None = None,
        today: bool = False,
        week: bool = False,
        limit: int | None = None,
        export: str | None = None,
    ) -> SearchResultSet:
        """Execute intelligent search over stored timeline events and return SearchResultSet."""
        start_time = time.perf_counter()

        search_filter = FilterValidator.process_filters(
            query=query,
            category=category,
            session_id=session,
            since=since,
            until=until,
            today=today,
            week=week,
            limit=limit,
            export=export,
        )

        db = self.storage.get_session()
        try:
            sql_query = self.query_builder.build_query(db, search_filter)
            db_records = sql_query.all()

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            results: list[SearchResultItem] = []
            for r in db_records:
                # Determine which field matched the query
                q_lower = (query or "").lower()
                matched_field = "summary"
                if q_lower and q_lower in (r.normalized_event_type or "").lower():
                    matched_field = "event_type"
                elif q_lower and q_lower in (r.source or "").lower():
                    matched_field = "source"
                elif q_lower and q_lower in (r.session_id or "").lower():
                    matched_field = "session_id"

                results.append(
                    SearchResultItem(
                        event_id=r.id,
                        timestamp=r.timestamp,
                        category=r.normalized_event_type or "Event",
                        source=r.source or "system",
                        actor_tool=r.actor_tool,
                        session_id=r.session_id,
                        summary=r.summary or "",
                        matched_field=matched_field,
                    )
                )

            applied = {}
            if category:
                applied["category"] = category
            if session:
                applied["session"] = session
            if today:
                applied["time_window"] = "today"
            elif week:
                applied["time_window"] = "week"
            if since:
                applied["since"] = str(since)
            if until:
                applied["until"] = str(until)
            if limit:
                applied["limit"] = limit

            return SearchResultSet(
                query=query or "",
                applied_filters=applied,
                total_results=len(results),
                execution_time_ms=elapsed_ms,
                results=results,
            )
        finally:
            db.close()
