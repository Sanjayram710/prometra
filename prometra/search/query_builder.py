import datetime
from typing import List, Optional
from sqlalchemy import or_, func
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, GitEventModel, AiEventModel
from prometra.search.models import SearchFilter
from prometra.core.time import utcnow

class SearchQueryBuilder:
    """Constructs parameterized SQLAlchemy queries for search execution."""

    def build_query(self, db_session, filters: SearchFilter):
        query = db_session.query(TimelineEventModel)
        
        # 1. Query keyword search using parameterized ilike
        if filters.query:
            search_pattern = f"%{filters.query}%"
            query = query.filter(
                or_(
                    TimelineEventModel.summary.ilike(search_pattern),
                    TimelineEventModel.normalized_event_type.ilike(search_pattern),
                    TimelineEventModel.source.ilike(search_pattern),
                    TimelineEventModel.actor_tool.ilike(search_pattern),
                    TimelineEventModel.session_id.ilike(search_pattern)
                )
            )

        # 2. Category filtering
        if filters.category:
            cat_lower = filters.category.lower()
            if cat_lower == "filesystem":
                query = query.filter(
                    or_(
                        TimelineEventModel.normalized_event_type.ilike("%filesystem%"),
                        TimelineEventModel.normalized_event_type.ilike("%file%")
                    )
                )
            elif cat_lower == "git":
                query = query.filter(TimelineEventModel.normalized_event_type.ilike("%git%"))
            elif cat_lower == "ai":
                query = query.filter(
                    or_(
                        TimelineEventModel.normalized_event_type.ilike("%ai%"),
                        TimelineEventModel.normalized_event_type.in_([
                            "PromptSubmitted", "PromptUpdated", "ResponseStarted", "ResponseReceived",
                            "ResponseCompleted", "ToolInvocationStarted", "ToolInvocationCompleted",
                            "ToolInvocationFailed", "ToolInvocation", "TokenUsage", "CostRecorded",
                            "ModelChanged", "ModelSelected", "ContextInjected", "ContextBuilt",
                            "LatencyMeasured", "ErrorOccurred", "RetryAttempt", "ai_event"
                        ]),
                        TimelineEventModel.source.ilike("%claude%"),
                        TimelineEventModel.actor_tool.isnot(None)
                    )
                )
            elif cat_lower == "session":
                query = query.filter(
                    or_(
                        TimelineEventModel.normalized_event_type.ilike("%session%"),
                        TimelineEventModel.normalized_event_type.in_(["SessionStarted", "SessionEnded"])
                    )
                )
            else:
                query = query.filter(TimelineEventModel.normalized_event_type.ilike(f"%{filters.category}%"))

        # 3. Session filtering
        if filters.session_id:
            query = query.filter(TimelineEventModel.session_id == filters.session_id)

        # 4. Time range filters
        now = utcnow()
        if filters.today:
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(TimelineEventModel.timestamp >= today_start)
        elif filters.week:
            week_start = now - datetime.timedelta(days=7)
            query = query.filter(TimelineEventModel.timestamp >= week_start)

        if filters.since:
            query = query.filter(TimelineEventModel.timestamp >= filters.since)
        if filters.until:
            query = query.filter(TimelineEventModel.timestamp <= filters.until)

        # 5. Sorting and Limit
        query = query.order_by(TimelineEventModel.timestamp.desc(), TimelineEventModel.sequence.desc())
        
        if filters.limit and filters.limit > 0:
            query = query.limit(filters.limit)

        return query
