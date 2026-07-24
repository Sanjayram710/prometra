import os
from typing import List, Dict, Any, Tuple, Optional
from prometra.intelligence.models import SessionSummary, AiUsageStats
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, AiEventModel, GitEventModel, SessionModel

EXT_TO_LANG = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "tsx": "TypeScript (React)",
    "jsx": "JavaScript (React)",
    "html": "HTML",
    "css": "CSS",
    "json": "JSON",
    "md": "Markdown",
    "yml": "YAML",
    "yaml": "YAML",
    "toml": "TOML",
    "sh": "Shell",
    "ps1": "PowerShell",
    "sql": "SQL",
}

class SummaryBuilder:
    """Extracts session events from SQLite database and builds structured SessionSummary and AiUsageStats."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def build_summary(self, session_id: Optional[str] = None) -> Tuple[SessionSummary, AiUsageStats, List[str], List[str], List[str]]:
        db = self.storage.get_session()
        try:
            # 1. Resolve session
            sess_rec = None
            if session_id:
                sess_rec = db.query(SessionModel).filter_by(session_id=session_id).first()
            if not sess_rec:
                sess_rec = db.query(SessionModel).order_by(SessionModel.start_ts.desc()).first()

            target_session_id = sess_rec.session_id if sess_rec else (session_id or "default")

            # 2. Query timeline events
            tl_query = db.query(TimelineEventModel)
            if target_session_id:
                tl_query = tl_query.filter(TimelineEventModel.session_id == target_session_id)
            tl_events = tl_query.all()

            total_events = len(tl_events)

            # Calculate duration
            duration_minutes = 0.0
            if sess_rec and sess_rec.duration_seconds:
                duration_minutes = round(sess_rec.duration_seconds / 60.0, 1)
            elif tl_events:
                timestamps = [e.timestamp for e in tl_events if e.timestamp]
                if len(timestamps) >= 2:
                    delta = max(timestamps) - min(timestamps)
                    duration_minutes = round(delta.total_seconds() / 60.0, 1)

            if duration_minutes <= 0.0:
                duration_minutes = 30.0  # Reasonable default for single point activity

            duration_hours = round(duration_minutes / 60.0, 2)

            # 3. Query Filesystem events
            fs_query = db.query(FilesystemEventModel)
            if target_session_id:
                fs_query = fs_query.filter(FilesystemEventModel.session_id == target_session_id)
            fs_events = fs_query.all()

            files_created = sum(1 for f in fs_events if f.operation == "created")
            files_modified = sum(1 for f in fs_events if f.operation == "modified")
            files_deleted = sum(1 for f in fs_events if f.operation == "deleted")

            # File path frequencies and languages
            file_counts: Dict[str, int] = {}
            lang_set = set()
            file_paths: List[str] = []

            for f in fs_events:
                path = f.normalized_relative_path or f.path
                if path:
                    file_paths.append(path)
                    file_counts[path] = file_counts.get(path, 0) + 1
                    ext = os.path.splitext(path)[1].lstrip(".").lower()
                    if ext in EXT_TO_LANG:
                        lang_set.add(EXT_TO_LANG[ext])

            top_files = [
                {"path": path, "count": count}
                for path, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]

            # 4. Query Git events
            git_query = db.query(GitEventModel)
            git_events = git_query.all()
            git_commits = len(git_events)
            commit_messages = [g.message for g in git_events if g.message]

            # 5. Query AI events
            ai_query = db.query(AiEventModel)
            if target_session_id:
                ai_query = ai_query.filter(AiEventModel.session_id == target_session_id)
            ai_records = ai_query.all()

            ai_prompts = sum(1 for a in ai_records if a.event_type in ("UserPrompt", "Prompt", "ai_prompt"))
            ai_tools = sum(1 for a in ai_records if a.event_type in ("ToolCall", "ToolResponse", "FileEdit"))
            prompts_text = [a.description for a in ai_records if a.description]

            # Calculate AI usage stats
            total_prompts = max(ai_prompts, len(prompts_text))
            est_tokens = total_prompts * 1250 + ai_tools * 850
            est_cost = round((est_tokens / 1000.0) * 0.003, 3)

            ai_usage = AiUsageStats(
                total_prompts=total_prompts,
                total_tool_calls=ai_tools,
                estimated_tokens=est_tokens,
                estimated_cost=est_cost,
                most_used_model="claude-3-5-sonnet",
                response_frequency_min=round(total_prompts / max(duration_minutes, 1.0), 2)
            )

            # Coding intensity
            events_per_min = total_events / max(duration_minutes, 1.0)
            if events_per_min > 1.5:
                intensity = "Very High"
            elif events_per_min > 0.8:
                intensity = "High"
            elif events_per_min > 0.3:
                intensity = "Moderate"
            else:
                intensity = "Low"

            # Most active period (window heuristic)
            if tl_events:
                first_ts = tl_events[0].timestamp
                if first_ts:
                    start_str = first_ts.strftime("%H:00")
                    end_str = (first_ts.replace(hour=(first_ts.hour + 1) % 24)).strftime("%H:00")
                    most_active = f"{start_str} - {end_str}"
                else:
                    most_active = "14:00 - 15:00"
            else:
                most_active = "14:00 - 15:00"

            summary = SessionSummary(
                session_id=target_session_id,
                duration_minutes=duration_minutes,
                duration_hours=duration_hours,
                total_events=total_events,
                files_created=files_created,
                files_modified=files_modified,
                files_deleted=files_deleted,
                git_commits=git_commits,
                ai_prompts=total_prompts,
                most_active_period=most_active,
                top_edited_files=top_files,
                languages=sorted(list(lang_set)) if lang_set else ["Python"],
                coding_intensity=intensity
            )

            return summary, ai_usage, commit_messages, prompts_text, file_paths
        finally:
            db.close()
