import uuid
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, GitEventModel

class TimelineEngine:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def append_event(self, event_data: dict):
        db = self.storage.get_session()
        try:
            max_seq = db.query(TimelineEventModel).count()
            
            # Create Specific Event
            specific_event_id = str(uuid.uuid4())
            event_type = event_data.get("type", "unknown")
            
            if event_type == "filesystem":
                fs_event = FilesystemEventModel(
                    event_id=specific_event_id,
                    session_id=event_data.get("session_id"),
                    project_id=event_data.get("project_id"),
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
                session_id=event_data.get("session_id"),
                related_event_ids=[specific_event_id] if event_type in ["filesystem", "git"] else [],
                summary=event_data.get("summary", "")
            )
            db.add(tl_event)
            db.commit()
        finally:
            db.close()

    def get_events(self, limit: int = 100, offset: int = 0, session_id: str = None, event_type: str = None, after_timestamp=None):
        db = self.storage.get_session()
        try:
            query = db.query(TimelineEventModel)
            if session_id:
                query = query.filter_by(session_id=session_id)
            if event_type:
                query = query.filter_by(normalized_event_type=event_type)
            if after_timestamp:
                query = query.filter(TimelineEventModel.timestamp >= after_timestamp)
                
            query = query.order_by(TimelineEventModel.sequence.asc())
            if limit > 0:
                query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)
                
            return query.all()
        finally:
            db.close()
            
    def get_related_event(self, event_id: str):
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
