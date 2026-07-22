import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, func
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, GitEventModel, SessionModel
from prometra.timeline.filters import TimelineFilter

class TimelineQueryEngine:
    """Executes optimized database queries for timeline event filtering and aggregation."""
    
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def build_query(self, db_session, filters: TimelineFilter):
        query = db_session.query(TimelineEventModel)
        
        # Filter by Session ID
        if filters.session_id:
            query = query.filter(TimelineEventModel.session_id == filters.session_id)
            
        # Filter by Event Type
        if filters.event_type:
            event_type_lower = filters.event_type.lower()
            if event_type_lower == "filesystem":
                query = query.filter(TimelineEventModel.normalized_event_type.ilike("%filesystem%"))
            elif event_type_lower == "git":
                query = query.filter(TimelineEventModel.normalized_event_type.ilike("%git%"))
            elif event_type_lower == "ai":
                query = query.filter(
                    or_(
                        TimelineEventModel.normalized_event_type.ilike("%ai%"),
                        TimelineEventModel.normalized_event_type.in_([
                            "PromptSubmitted", "ResponseReceived", "ToolInvocation",
                            "ModelSelected", "ContextBuilt", "TokenUsage",
                            "LatencyMeasured", "SessionStarted", "SessionEnded",
                            "ErrorOccurred", "ai_event"
                        ]),
                        TimelineEventModel.source.ilike("%claude%"),
                        TimelineEventModel.actor_tool.isnot(None)
                    )
                )
            elif event_type_lower == "connector":
                query = query.filter(
                    or_(
                        TimelineEventModel.normalized_event_type.ilike("%connector%"),
                        TimelineEventModel.actor_tool.isnot(None)
                    )
                )
            elif event_type_lower == "session":
                query = query.filter(
                    or_(
                        TimelineEventModel.normalized_event_type.ilike("%session%"),
                        TimelineEventModel.normalized_event_type.in_(["SessionStarted", "SessionEnded"])
                    )
                )
            else:
                query = query.filter(TimelineEventModel.normalized_event_type.ilike(f"%{filters.event_type}%"))
                
        # Filter by Connector Name
        if filters.connector:
            connector_pattern = f"%{filters.connector}%"
            query = query.filter(
                or_(
                    TimelineEventModel.actor_tool.ilike(connector_pattern),
                    TimelineEventModel.source.ilike(connector_pattern)
                )
            )
            
        # Filter by Search term
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.filter(
                or_(
                    TimelineEventModel.summary.ilike(search_pattern),
                    TimelineEventModel.normalized_event_type.ilike(search_pattern),
                    TimelineEventModel.source.ilike(search_pattern),
                    TimelineEventModel.actor_tool.ilike(search_pattern)
                )
            )
            
        # Filter by Today
        if filters.today:
            today_start = datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(TimelineEventModel.timestamp >= today_start)
            
        # Sorting
        if filters.reverse:
            query = query.order_by(TimelineEventModel.sequence.desc(), TimelineEventModel.id.desc())
        else:
            query = query.order_by(TimelineEventModel.sequence.asc(), TimelineEventModel.id.asc())
            
        return query

    def fetch_events(self, filters: TimelineFilter) -> List[TimelineEventModel]:
        """Fetch timeline events matching filters with pagination."""
        db = self.storage.get_session()
        try:
            query = self.build_query(db, filters)
            
            if filters.offset > 0:
                query = query.offset(filters.offset)
            if filters.limit is not None and filters.limit > 0:
                query = query.limit(filters.limit)
                
            return query.all()
        finally:
            db.close()

    def fetch_summary(self, filters: TimelineFilter) -> Dict[str, Any]:
        """Compute aggregated summary statistics for events matching filters."""
        db = self.storage.get_session()
        try:
            query = self.build_query(db, filters)
            events = query.all()
            
            total_events = len(events)
            sessions = set()
            files_modified = 0
            git_commits = 0
            ai_events = 0
            connectors = set()
            
            for e in events:
                if e.session_id:
                    sessions.add(e.session_id)
                if e.actor_tool:
                    connectors.add(e.actor_tool)
                elif e.source and e.source not in ("filesystem", "git", "system"):
                    connectors.add(e.source)
                    
                net = (e.normalized_event_type or "").lower()
                if "filesystem" in net:
                    files_modified += 1
                elif "git" in net:
                    git_commits += 1
                elif "ai" in net or net in [
                    "promptsubmitted", "responsereceived", "toolinvocation",
                    "modelselected", "contextbuilt", "tokenusage",
                    "latencymeasured", "sessionstarted", "sessionended",
                    "erroroccurred"
                ] or e.actor_tool:
                    ai_events += 1
                    
            # Also check session count from SessionModel if session set is empty but total sessions in DB exist
            if not sessions and not filters.session_id and not filters.search and not filters.event_type:
                all_sessions_count = db.query(SessionModel).count()
                sessions_count = all_sessions_count
            else:
                sessions_count = len(sessions)
                
            return {
                "total_events": total_events,
                "sessions_count": sessions_count,
                "files_modified": files_modified,
                "git_commits": git_commits,
                "ai_events": ai_events,
                "connectors_used": sorted(list(connectors))
            }
        finally:
            db.close()

    def fetch_grouped_by_session(self, filters: TimelineFilter) -> List[Dict[str, Any]]:
        """Fetch timeline events grouped by session ID."""
        db = self.storage.get_session()
        try:
            events = self.fetch_events(filters)
            
            grouped: Dict[str, List[TimelineEventModel]] = {}
            for e in events:
                sess_id = e.session_id or "unassigned"
                if sess_id not in grouped:
                    grouped[sess_id] = []
                grouped[sess_id].append(e)
                
            result = []
            for sess_id, sess_events in grouped.items():
                sess_model = db.query(SessionModel).filter_by(session_id=sess_id).first() if sess_id != "unassigned" else None
                
                duration = sess_model.duration_seconds if sess_model and sess_model.duration_seconds else 0
                if not duration and len(sess_events) > 1:
                    start = sess_events[0].timestamp
                    end = sess_events[-1].timestamp
                    if start and end:
                        duration = int(abs((end - start).total_seconds()))
                        
                files_changed = sum(1 for e in sess_events if "filesystem" in (e.normalized_event_type or "").lower())
                git_commits = sum(1 for e in sess_events if "git" in (e.normalized_event_type or "").lower())
                ai_events = sum(1 for e in sess_events if "ai" in (e.normalized_event_type or "").lower() or e.actor_tool or (e.normalized_event_type or "") in [
                    "PromptSubmitted", "ResponseReceived", "ToolInvocation", "ModelSelected", "ContextBuilt", "TokenUsage", "LatencyMeasured"
                ])
                
                result.append({
                    "session_id": sess_id,
                    "duration_seconds": duration,
                    "files_changed": files_changed,
                    "git_commits": git_commits,
                    "ai_events": ai_events,
                    "events": sess_events
                })
            return result
        finally:
            db.close()
