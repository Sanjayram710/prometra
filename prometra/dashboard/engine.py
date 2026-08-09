import contextlib
import datetime

from prometra.core.time import utcnow
from prometra.dashboard.metrics import (
    ActivityMetrics,
    AiMetrics,
    DashboardMetrics,
    FilesystemMetrics,
    GitMetrics,
    SessionMetrics,
    TopFileEntry,
    TopModelEntry,
)
from prometra.storage.models import (
    AiEventModel,
    FilesystemEventModel,
    GitEventModel,
    SessionModel,
    TimelineEventModel,
)
from prometra.storage.sqlite import SQLiteStorage


class DashboardEngine:
    """Computes analytics dashboard metrics using optimized SQLite aggregation queries."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def compute_metrics(
        self,
        today: bool = False,
        week: bool = False,
        month: bool = False,
        session_id: str | None = None,
    ) -> DashboardMetrics:
        db = self.storage.get_session()
        try:
            # Determine time boundary filter
            now = utcnow()
            start_boundary: datetime.datetime | None = None
            filter_label = "All Time"

            if today:
                start_boundary = now.replace(hour=0, minute=0, second=0, microsecond=0)
                filter_label = "Today"
            elif week:
                start_boundary = now - datetime.timedelta(days=7)
                filter_label = "Past 7 Days"
            elif month:
                start_boundary = now - datetime.timedelta(days=30)
                filter_label = "Past 30 Days"
            elif session_id:
                filter_label = f"Session #{session_id}"

            # 1. Session Metrics
            sess_query = db.query(SessionModel)
            if start_boundary:
                sess_query = sess_query.filter(SessionModel.start_ts >= start_boundary)
            if session_id:
                sess_query = sess_query.filter(SessionModel.session_id == session_id)

            sessions_list = sess_query.all()
            total_sessions = len(sessions_list)
            durations = [
                s.duration_seconds for s in sessions_list if s.duration_seconds
            ]

            total_duration = sum(durations) if durations else 0
            longest_session = max(durations) if durations else 0
            avg_session = int(total_duration / len(durations)) if durations else 0

            # 2. Filesystem Metrics
            fs_query = db.query(FilesystemEventModel)
            if start_boundary:
                fs_query = fs_query.filter(
                    FilesystemEventModel.timestamp >= start_boundary
                )
            if session_id:
                fs_query = fs_query.filter(
                    FilesystemEventModel.session_id == session_id
                )

            fs_events = fs_query.all()
            files_created = sum(
                1
                for e in fs_events
                if (e.operation or "").lower() in ["created", "create"]
            )
            files_modified = sum(
                1
                for e in fs_events
                if (e.operation or "").lower() in ["modified", "modify", "change"]
            )
            files_deleted = sum(
                1
                for e in fs_events
                if (e.operation or "").lower() in ["deleted", "delete", "removed"]
            )

            # Top Edited Files
            file_counts: dict[str, int] = {}
            for e in fs_events:
                path = e.normalized_relative_path or e.path or "unknown"
                file_counts[path] = file_counts.get(path, 0) + 1

            sorted_files = sorted(
                file_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            top_edited_files = [TopFileEntry(path=k, edits=v) for k, v in sorted_files]

            # 3. Git Metrics
            git_query = db.query(GitEventModel)
            if start_boundary:
                git_query = git_query.filter(GitEventModel.timestamp >= start_boundary)

            git_commits = git_query.count()
            days_span = 1
            if start_boundary:
                days_span = max((now - start_boundary).days, 1)
            commits_per_day = round(git_commits / days_span, 2)

            # 4. AI Metrics
            ai_query = db.query(AiEventModel)
            if start_boundary:
                ai_query = ai_query.filter(AiEventModel.timestamp >= start_boundary)
            if session_id:
                ai_query = ai_query.filter(AiEventModel.session_id == session_id)

            ai_records = ai_query.all()
            ai_prompts = sum(
                1 for r in ai_records if "prompt" in (r.event_type or "").lower()
            )
            ai_responses = sum(
                1 for r in ai_records if "response" in (r.event_type or "").lower()
            )
            tool_calls = sum(
                1 for r in ai_records if "tool" in (r.event_type or "").lower()
            )
            errors = sum(
                1
                for r in ai_records
                if "error" in (r.event_type or "").lower()
                or "fail" in (r.event_type or "").lower()
            )
            retries = sum(
                1 for r in ai_records if "retry" in (r.event_type or "").lower()
            )

            p_tokens = 0
            c_tokens = 0
            t_tokens = 0
            est_cost = 0.0
            connectors = set()
            model_counts: dict[str, int] = {}

            for r in ai_records:
                if r.connector:
                    connectors.add(r.connector)
                if r.model_name:
                    model_counts[r.model_name] = model_counts.get(r.model_name, 0) + 1
                if r.cost:
                    est_cost += r.cost
                if r.token_usage and isinstance(r.token_usage, dict):
                    in_t = r.token_usage.get("prompt_tokens", 0)
                    out_t = r.token_usage.get("completion_tokens", 0)
                    tot_t = r.token_usage.get("total_tokens", 0) or (in_t + out_t)
                    p_tokens += in_t
                    c_tokens += out_t
                    t_tokens += tot_t

            sorted_models = sorted(
                model_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            top_models = [
                TopModelEntry(model_name=k, count=v) for k, v in sorted_models
            ]

            # 5. Activity Pattern Metrics
            tl_query = db.query(TimelineEventModel)
            if start_boundary:
                tl_query = tl_query.filter(
                    TimelineEventModel.timestamp >= start_boundary
                )
            if session_id:
                tl_query = tl_query.filter(TimelineEventModel.session_id == session_id)

            tl_events = tl_query.all()
            hour_counts: dict[int, int] = {}
            daily_activity: dict[str, int] = {}

            for e in tl_events:
                if e.timestamp:
                    with contextlib.suppress(AttributeError, ValueError):
                        h = e.timestamp.hour
                        hour_counts[h] = hour_counts.get(h, 0) + 1
                        day_key = e.timestamp.strftime("%Y-%m-%d")
                        daily_activity[day_key] = daily_activity.get(day_key, 0) + 1

            top_active_hours = sorted(
                hour_counts.keys(), key=lambda k: hour_counts[k], reverse=True
            )[:3]

            return DashboardMetrics(
                filter_label=filter_label,
                sessions=SessionMetrics(
                    total_sessions=total_sessions,
                    total_duration_seconds=total_duration,
                    longest_session_seconds=longest_session,
                    avg_session_length_seconds=avg_session,
                ),
                filesystem=FilesystemMetrics(
                    files_created=files_created,
                    files_modified=files_modified,
                    files_deleted=files_deleted,
                    top_edited_files=top_edited_files,
                ),
                git=GitMetrics(
                    total_commits=git_commits, commits_per_day=commits_per_day
                ),
                ai=AiMetrics(
                    ai_prompts=ai_prompts,
                    ai_responses=ai_responses,
                    tool_calls=tool_calls,
                    errors=errors,
                    retries=retries,
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    total_tokens=t_tokens,
                    estimated_cost=round(est_cost, 4),
                    avg_response_time_ms=0.0,
                    top_models=top_models,
                    connectors_used=sorted(connectors),
                ),
                activity=ActivityMetrics(
                    top_active_hours=top_active_hours, daily_activity=daily_activity
                ),
            )
        finally:
            db.close()
