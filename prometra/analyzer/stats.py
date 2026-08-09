from prometra.storage.models import (
    FilesystemEventModel,
    SessionModel,
    TimelineEventModel,
)
from prometra.storage.sqlite import SQLiteStorage


class StatsCalculator:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def compute_project_stats(self, project_id: str):
        db = self.storage.get_session()
        try:
            sessions = db.query(SessionModel).filter_by(project_id=project_id).count()
            fs_events = (
                db.query(FilesystemEventModel).filter_by(project_id=project_id).count()
            )

            # Since git events don't have project_id directly, we find via timeline
            git_events_count = 0
            # For V1, we just count timeline events with type git
            git_events_count = (
                db.query(TimelineEventModel)
                .filter_by(normalized_event_type="git")
                .count()
            )

            langs = {}
            for fs in (
                db.query(FilesystemEventModel)
                .filter_by(project_id=project_id, operation="modified")
                .all()
            ):
                ext = fs.path.split(".")[-1] if "." in fs.path else "unknown"
                langs[ext] = langs.get(ext, 0) + 1

            return {
                "total_sessions": sessions,
                "total_file_events": fs_events,
                "total_git_events": git_events_count,
                "language_distribution": langs,
                "dependency_changes": langs.get("json", 0)
                + langs.get("toml", 0)
                + langs.get("yaml", 0),
            }
        finally:
            db.close()
