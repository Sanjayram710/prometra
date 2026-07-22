import uuid
from typing import List, Dict, Any, Optional
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, GitEventModel
from prometra.timeline.filters import TimelineFilter
from prometra.timeline.queries import TimelineQueryEngine
from prometra.timeline.formatter import TimelineFormatter
from prometra.timeline.summary import TimelineSummaryGenerator, SummaryMetrics

class TimelineEngine:
    """Core engine for timeline recording, querying, filtering, summary, and formatting."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.query_engine = TimelineQueryEngine(storage)
        self.summary_generator = TimelineSummaryGenerator(self.query_engine)

    def append_event(self, event_data: dict):
        """Record a timeline event and any underlying specific event."""
        db = self.storage.get_session()
        try:
            max_seq = db.query(TimelineEventModel).count()
            
            # Create Specific Event
            specific_event_id = str(uuid.uuid4())
            event_type = event_data.get("type", "unknown")
            
            if event_type == "filesystem":
                fs_event = FilesystemEventModel(
                    event_id=specific_event_id,
                    session_id=event_data.get("session_id") or "default_session",
                    project_id=event_data.get("project_id") or "default_project",
                    timestamp=event_data.get("timestamp"),
                    path=event_data.get("path"),
                    normalized_relative_path=event_data.get("normalized_relative_path"),
                    operation=event_data.get("operation"),
                    source=event_data.get("source", "filesystem")
                )
                db.add(fs_event)
            elif event_type == "git":
                git_event = GitEventModel(
                    event_id=specific_event_id,
                    repository=event_data.get("repository"),
                    branch=event_data.get("branch"),
                    commit_id=event_data.get("commit_id"),
                    author=event_data.get("author"),
                    message=event_data.get("message"),
                    timestamp=event_data.get("timestamp"),
                    insertions=event_data.get("insertions", 0),
                    deletions=event_data.get("deletions", 0),
                    changed_files=event_data.get("changed_files", []),
                    merge_flag=event_data.get("merge_flag", False),
                    tag=event_data.get("tag"),
                    parent_commits=event_data.get("parent_commits", []),
                    source=event_data.get("source", "git")
                )
                db.add(git_event)
            
            # Create Unified Timeline Event
            tl_event = TimelineEventModel(
                normalized_event_type=event_type,
                timestamp=event_data.get("timestamp"),
                sequence=max_seq + 1,
                source=event_data.get("source", "system"),
                actor_tool=event_data.get("actor_tool") or event_data.get("connector_name"),
                session_id=event_data.get("session_id"),
                related_event_ids=[specific_event_id] if event_type in ["filesystem", "git"] else [],
                summary=event_data.get("summary", "")
            )
            db.add(tl_event)
            db.commit()
        finally:
            db.close()

    def get_events(
        self,
        limit: Optional[int] = 100,
        offset: int = 0,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        after_timestamp=None,
        connector: Optional[str] = None,
        search: Optional[str] = None,
        today: bool = False,
        reverse: bool = False
    ) -> List[TimelineEventModel]:
        """Fetch filtered timeline events (backwards-compatible API)."""
        filters = TimelineFilter(
            session_id=session_id,
            event_type=event_type,
            connector=connector,
            search=search,
            today=today,
            limit=limit,
            offset=offset,
            reverse=reverse
        )
        events = self.query_engine.fetch_events(filters)
        if after_timestamp:
            events = [e for e in events if e.timestamp and e.timestamp >= after_timestamp]
        return events

    def query_events(self, filters: TimelineFilter) -> List[TimelineEventModel]:
        """Execute query using TimelineFilter model."""
        return self.query_engine.fetch_events(filters)

    def get_summary(self, filters: TimelineFilter) -> SummaryMetrics:
        """Generate timeline summary metrics."""
        return self.summary_generator.generate(filters)

    def get_grouped(self, filters: TimelineFilter) -> List[Dict[str, Any]]:
        """Fetch timeline events grouped by session."""
        return self.query_engine.fetch_grouped_by_session(filters)

    def export_events(self, filters: TimelineFilter, export_path: str) -> str:
        """Export timeline events to specified file path."""
        events = self.query_engine.fetch_events(filters)
        return TimelineFormatter.export_to_file(events, export_path)

    def get_related_event(self, event_id: str):
        """Retrieve full details of specific filesystem or git event."""
        db = self.storage.get_session()
        try:
            fs_event = db.query(FilesystemEventModel).filter_by(event_id=event_id).first()
            if fs_event:
                return fs_event
            git_event = db.query(GitEventModel).filter_by(event_id=event_id).first()
            if git_event:
                return git_event
            return None
        finally:
            db.close()
