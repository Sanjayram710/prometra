from typing import Tuple, Optional, Dict, Any, List
from sqlalchemy import func
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import SessionModel, TimelineEventModel, FilesystemEventModel, GitEventModel, AiEventModel
from prometra.compare.models import SessionStats, CompareResult

class CompareEngine:
    """Engine for querying session metrics and computing session comparisons."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def resolve_latest_sessions(self) -> Tuple[str, str]:
        """Resolve the two most recent distinct session IDs from database history."""
        db = self.storage.get_session()
        try:
            # Fetch sessions ordered by start_ts descending
            sessions = (
                db.query(SessionModel)
                .order_by(SessionModel.start_ts.desc())
                .all()
            )
            sess_ids = [s.session_id for s in sessions if s.session_id]

            # Fallback: check TimelineEventModel for distinct session_ids if < 2 found in SessionModel
            if len(sess_ids) < 2:
                tl_sessions = (
                    db.query(TimelineEventModel.session_id)
                    .filter(TimelineEventModel.session_id.isnot(None))
                    .distinct()
                    .all()
                )
                for (sid,) in tl_sessions:
                    if sid and sid not in sess_ids:
                        sess_ids.append(sid)

            if len(sess_ids) < 2:
                raise ValueError("At least two sessions are required to compare using --latest.")

            # Session B is the latest session, Session A is the 2nd latest
            session_b = sess_ids[0]
            session_a = sess_ids[1]
            return session_a, session_b
        finally:
            db.close()

    def get_session_stats(self, session_id: str) -> SessionStats:
        """Fetch metrics and activity stats for a specific session."""
        db = self.storage.get_session()
        try:
            sess_model = db.query(SessionModel).filter_by(session_id=session_id).first()
            tl_events = db.query(TimelineEventModel).filter_by(session_id=session_id).order_by(TimelineEventModel.id.asc()).all()

            if not sess_model and not tl_events:
                raise ValueError(f"Session '{session_id}' not found.")

            # Duration calculation
            duration_sec = 0
            if sess_model and sess_model.duration_seconds:
                duration_sec = sess_model.duration_seconds
            elif len(tl_events) > 1:
                start = tl_events[0].timestamp
                end = tl_events[-1].timestamp
                if start and end:
                    duration_sec = int(abs((end - start).total_seconds()))

            duration_min = round(duration_sec / 60)

            # Filesystem metrics
            fs_events = db.query(FilesystemEventModel).filter_by(session_id=session_id).all()
            files_created = sum(1 for e in fs_events if (e.operation or "").lower() in ["created", "create"])
            files_modified = sum(1 for e in fs_events if (e.operation or "").lower() in ["modified", "modify", "change"])
            files_deleted = sum(1 for e in fs_events if (e.operation or "").lower() in ["deleted", "delete", "removed"])

            # Fallback to TimelineEventModel if FilesystemEventModel empty
            if not fs_events:
                for e in tl_events:
                    net = (e.normalized_event_type or "").lower()
                    if "filesystem" in net or "file" in net:
                        sum_lower = (e.summary or "").lower()
                        if "created" in sum_lower or "create" in sum_lower:
                            files_created += 1
                        elif "deleted" in sum_lower or "delete" in sum_lower or "removed" in sum_lower:
                            files_deleted += 1
                        else:
                            files_modified += 1

            # Git metrics
            git_commits = db.query(GitEventModel).count() # query git events
            git_events_session = sum(1 for e in tl_events if "git" in (e.normalized_event_type or "").lower())
            if git_events_session > 0:
                git_commits = git_events_session
            else:
                # check GitEventModel for session matching if any
                git_commits = sum(1 for e in tl_events if "commit" in (e.summary or "").lower() or "git" in (e.source or "").lower())

            # AI metrics
            ai_events_count = db.query(AiEventModel).filter_by(session_id=session_id).count()
            if ai_events_count == 0:
                ai_events_count = sum(
                    1 for e in tl_events 
                    if any(k in (e.normalized_event_type or "").lower() for k in ["ai", "prompt", "response", "tool", "model", "token"]) 
                    or (e.actor_tool and e.actor_tool != "system")
                )

            # Event distribution
            event_types: Dict[str, int] = {}
            for e in tl_events:
                etype = e.normalized_event_type or "unknown"
                event_types[etype] = event_types.get(etype, 0) + 1

            total_events = len(tl_events)

            # Productivity metrics
            duration_minutes_non_zero = max(duration_min, 1)
            productivity = {
                "events_per_minute": round(total_events / duration_minutes_non_zero, 2),
                "files_changed_per_minute": round((files_created + files_modified + files_deleted) / duration_minutes_non_zero, 2),
                "commits_per_hour": round((git_commits * 60) / duration_minutes_non_zero, 2)
            }

            start_ts_str = str(sess_model.start_ts) if sess_model and sess_model.start_ts else (str(tl_events[0].timestamp) if tl_events else None)

            return SessionStats(
                session_id=session_id,
                start_ts=start_ts_str,
                duration_seconds=duration_sec,
                duration_minutes=duration_min,
                files_created=files_created,
                files_modified=files_modified,
                files_deleted=files_deleted,
                git_commits=git_commits,
                ai_events=ai_events_count,
                total_events=total_events,
                productivity_metrics=productivity,
                event_type_distribution=event_types
            )
        finally:
            db.close()

    def compare_sessions(
        self,
        session_a: Optional[str] = None,
        session_b: Optional[str] = None,
        latest: bool = False
    ) -> CompareResult:
        """Compare two sessions and return metric differences."""
        if latest:
            resolved_a, resolved_b = self.resolve_latest_sessions()
            session_a = session_a or resolved_a
            session_b = session_b or resolved_b

        if not session_a or not session_b:
            raise ValueError("Two session IDs are required for comparison (or use --latest).")

        if session_a == session_b:
            raise ValueError(f"Cannot compare session '{session_a}' with itself.")

        stats_a = self.get_session_stats(session_a)
        stats_b = self.get_session_stats(session_b)

        dur_sec_diff = stats_b.duration_seconds - stats_a.duration_seconds
        dur_min_diff = stats_b.duration_minutes - stats_a.duration_minutes
        
        dur_diff_str = f"+{dur_min_diff} min" if dur_min_diff >= 0 else f"{dur_min_diff} min"

        files_created_diff = stats_b.files_created - stats_a.files_created
        files_modified_diff = stats_b.files_modified - stats_a.files_modified
        files_deleted_diff = stats_b.files_deleted - stats_a.files_deleted
        git_commit_diff = stats_b.git_commits - stats_a.git_commits
        ai_event_diff = stats_b.ai_events - stats_a.ai_events
        total_events_diff = stats_b.total_events - stats_a.total_events

        timeline_diff = {
            "total_events_a": stats_a.total_events,
            "total_events_b": stats_b.total_events,
            "total_events_difference": total_events_diff,
            "event_type_distribution_a": stats_a.event_type_distribution,
            "event_type_distribution_b": stats_b.event_type_distribution,
            "productivity_a": stats_a.productivity_metrics,
            "productivity_b": stats_b.productivity_metrics
        }

        return CompareResult(
            session_a=session_a,
            session_b=session_b,
            stats_a=stats_a,
            stats_b=stats_b,
            duration_difference=dur_diff_str,
            duration_seconds_difference=dur_sec_diff,
            files_created_difference=files_created_diff,
            files_modified_difference=files_modified_diff,
            files_deleted_difference=files_deleted_diff,
            git_commit_difference=git_commit_diff,
            ai_event_difference=ai_event_diff,
            total_events_difference=total_events_diff,
            timeline_difference=timeline_diff
        )
