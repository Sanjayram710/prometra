import datetime
import uuid
from typing import Any

from prometra.ai.events import AiEvent
from prometra.connectors.events import BaseEvent, EventBus
from prometra.core.time import utcnow
from prometra.storage.models import (
    AiEventModel,
    FilesystemEventModel,
    GitEventModel,
    TimelineEventModel,
)
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.filters import TimelineFilter
from prometra.timeline.formatter import TimelineFormatter
from prometra.timeline.queries import TimelineQueryEngine
from prometra.timeline.summary import SummaryMetrics, TimelineSummaryGenerator


class TimelineEngine:
    """Core engine for timeline recording, querying, filtering, summary, and formatting."""

    def __init__(self, storage: SQLiteStorage, event_bus: EventBus | None = None):
        self.storage = storage
        self.query_engine = TimelineQueryEngine(storage)
        self.summary_generator = TimelineSummaryGenerator(self.query_engine)
        self._event_bus = None
        if event_bus:
            self.attach_event_bus(event_bus)

    def attach_event_bus(self, event_bus: EventBus):
        """Subscribe to event bus for automatic AI event persistence."""
        self._event_bus = event_bus
        self._event_bus.subscribe("*", self.handle_bus_event)

    def handle_bus_event(self, event: BaseEvent):
        """Handler for events published on EventBus."""
        if isinstance(event, AiEvent):
            self.append_ai_event(event)

    def append_ai_event(self, ai_event: AiEvent):
        """Persist a generic AI event in AiEventModel and unified TimelineEventModel."""
        db = self.storage.get_session()
        try:
            max_seq = db.query(TimelineEventModel).count()
            specific_event_id = str(uuid.uuid4())

            # Parse timestamp if string or datetime
            if isinstance(ai_event.timestamp, str) and ai_event.timestamp:
                try:
                    ts = datetime.datetime.fromisoformat(ai_event.timestamp)
                except (ValueError, TypeError):
                    ts = utcnow()
            elif isinstance(ai_event.timestamp, datetime.datetime):
                ts = ai_event.timestamp
            else:
                ts = utcnow()

            token_dict = ai_event.tokens.model_dump() if ai_event.tokens else None
            desc = ai_event.get_description()

            # Save in AiEventModel
            ai_db_record = AiEventModel(
                event_id=specific_event_id,
                session_id=ai_event.session_id,
                timestamp=ts,
                event_type=ai_event.event_type,
                connector=ai_event.connector_name,
                model_name=ai_event.model_name,
                prompt_id=ai_event.prompt_id,
                tool_name=ai_event.tool_name,
                token_usage=token_dict,
                cost=ai_event.cost,
                description=desc,
                extra_metadata=ai_event.metadata,
            )
            db.add(ai_db_record)

            # Save in unified TimelineEventModel
            tl_event = TimelineEventModel(
                normalized_event_type=ai_event.event_type,
                timestamp=ts,
                sequence=max_seq + 1,
                source=ai_event.connector_name,
                actor_tool=ai_event.connector_name,
                session_id=ai_event.session_id,
                related_event_ids=[specific_event_id],
                summary=desc,
            )
            db.add(tl_event)
            db.commit()
        finally:
            db.close()

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
                    path=event_data.get("path") or "unknown",
                    normalized_relative_path=event_data.get("normalized_relative_path")
                    or "unknown",
                    operation=event_data.get("operation") or "modified",
                    source=event_data.get("source", "filesystem"),
                )
                db.add(fs_event)
            elif event_type == "git":
                git_event = GitEventModel(
                    event_id=specific_event_id,
                    repository=event_data.get("repository") or "default_repo",
                    branch=event_data.get("branch") or "main",
                    commit_id=event_data.get("commit_id") or "0000000",
                    author=event_data.get("author"),
                    message=event_data.get("message"),
                    timestamp=event_data.get("timestamp"),
                    insertions=event_data.get("insertions", 0),
                    deletions=event_data.get("deletions", 0),
                    changed_files=event_data.get("changed_files", []),
                    merge_flag=event_data.get("merge_flag", False),
                    tag=event_data.get("tag"),
                    parent_commits=event_data.get("parent_commits", []),
                    source=event_data.get("source", "git"),
                )
                db.add(git_event)

            # Normalize event type
            if event_type == "session":
                sum_lower = (event_data.get("summary") or "").lower()
                if "start" in sum_lower:
                    norm_type = "SessionStarted"
                elif "end" in sum_lower:
                    norm_type = "SessionEnded"
                else:
                    norm_type = "session"
            else:
                norm_type = event_type

            # Create Unified Timeline Event
            tl_event = TimelineEventModel(
                normalized_event_type=norm_type,
                timestamp=event_data.get("timestamp") or utcnow(),
                sequence=max_seq + 1,
                source=event_data.get("source", "system"),
                actor_tool=event_data.get("actor_tool")
                or event_data.get("connector_name"),
                session_id=event_data.get("session_id"),
                related_event_ids=[specific_event_id]
                if event_type in ["filesystem", "git"]
                else [],
                summary=event_data.get("summary", ""),
            )
            db.add(tl_event)
            db.commit()
        finally:
            db.close()

    def get_events(
        self,
        limit: int | None = 100,
        offset: int = 0,
        session_id: str | None = None,
        event_type: str | None = None,
        after_timestamp=None,
        connector: str | None = None,
        search: str | None = None,
        today: bool = False,
        reverse: bool = False,
    ) -> list[TimelineEventModel]:
        """Fetch filtered timeline events (backwards-compatible API)."""
        filters = TimelineFilter(
            session_id=session_id,
            event_type=event_type,
            connector=connector,
            search=search,
            today=today,
            limit=limit,
            offset=offset,
            reverse=reverse,
        )
        events = self.query_engine.fetch_events(filters)
        if after_timestamp:
            events = [
                e for e in events if e.timestamp and e.timestamp >= after_timestamp
            ]
        return events

    def query_events(self, filters: TimelineFilter) -> list[TimelineEventModel]:
        """Execute query using TimelineFilter model."""
        return self.query_engine.fetch_events(filters)

    def get_summary(self, filters: TimelineFilter) -> SummaryMetrics:
        """Generate timeline summary metrics."""
        return self.summary_generator.generate(filters)

    def get_grouped(self, filters: TimelineFilter) -> list[dict[str, Any]]:
        """Fetch timeline events grouped by session."""
        return self.query_engine.fetch_grouped_by_session(filters)

    def export_events(self, filters: TimelineFilter, export_path: str) -> str:
        """Export timeline events to specified file path."""
        events = self.query_engine.fetch_events(filters)
        return TimelineFormatter.export_to_file(events, export_path)

    def get_related_event(self, event_id: str):
        """Retrieve full details of specific event."""
        db = self.storage.get_session()
        try:
            ai_event = db.query(AiEventModel).filter_by(event_id=event_id).first()
            if ai_event:
                return ai_event
            fs_event = (
                db.query(FilesystemEventModel).filter_by(event_id=event_id).first()
            )
            if fs_event:
                return fs_event
            git_event = db.query(GitEventModel).filter_by(event_id=event_id).first()
            if git_event:
                return git_event
            return None
        finally:
            db.close()
