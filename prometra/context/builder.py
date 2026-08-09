import uuid

from prometra.analyzer.health import HealthAnalyzer
from prometra.analyzer.stats import StatsCalculator
from prometra.context.models import (
    AnalyzerSummary,
    Context,
    FileChange,
    GitSnapshot,
    ProjectState,
    RepositorySummary,
    SessionSummary,
    TimelineSummary,
)
from prometra.core.time import utcnow
from prometra.storage.models import FilesystemEventModel, GitEventModel, SessionModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine


class ContextBuilder:
    """Assembles V1 data into structured, read-only V2 Context models."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.stats_calculator = StatsCalculator(storage)
        self.health_analyzer = HealthAnalyzer(storage)
        self.timeline_engine = TimelineEngine(storage)

    def build_context(
        self, project_id: str, project_path: str, session_id: str | None = None
    ) -> Context:
        db = self.storage.get_session()
        try:
            # 1. Repository Summary
            repo_summary = RepositorySummary(
                project_id=project_id, root_path=project_path
            )

            # 2. Session Summary
            session_summary = None
            if session_id:
                s_model = (
                    db.query(SessionModel).filter_by(session_id=session_id).first()
                )
                if s_model:
                    session_summary = SessionSummary(
                        session_id=s_model.session_id,
                        duration_seconds=s_model.duration_seconds or 0,
                        started_at=str(s_model.start_ts),
                        warnings=s_model.warnings or [],
                    )
            else:
                s_model = (
                    db.query(SessionModel)
                    .filter_by(project_id=project_id, status="active")
                    .first()
                )
                if s_model:
                    session_summary = SessionSummary(
                        session_id=s_model.session_id,
                        duration_seconds=s_model.duration_seconds or 0,
                        started_at=str(s_model.start_ts),
                        warnings=s_model.warnings or [],
                    )

            sid = session_summary.session_id if session_summary else None

            # 3. Git Snapshot
            git_snapshot = None
            git_events = (
                db.query(GitEventModel)
                .order_by(GitEventModel.timestamp.desc())
                .limit(1)
                .all()
            )
            if git_events:
                last_git = git_events[0]
                git_snapshot = GitSnapshot(
                    branch=last_git.branch,
                    commit_id=last_git.commit_id,
                    changed_files=last_git.changed_files or [],
                )

            # 4. Recent Files (last 10 modifications in current session or overall)
            recent_files = []
            fs_query = db.query(FilesystemEventModel)
            if sid:
                fs_query = fs_query.filter_by(session_id=sid)
            fs_events = (
                fs_query.order_by(FilesystemEventModel.timestamp.desc()).limit(10).all()
            )
            for f in fs_events:
                recent_files.append(
                    FileChange(
                        path=f.normalized_relative_path or f.path,
                        operation=f.operation,
                        timestamp=str(f.timestamp),
                    )
                )

            # 5. Analyzer
            health_res = self.health_analyzer.analyze(project_id)
            analyzer_summary = AnalyzerSummary(
                health_score=health_res["score"],
                risk_level=health_res["severity"],
                recommendation=health_res["recommendation"],
                findings=health_res["findings"],
            )

            # 6. Timeline Summary
            timeline_events = self.timeline_engine.get_events(limit=20, session_id=sid)
            timeline_summary = TimelineSummary(
                total_events=len(timeline_events),
                recent_events=[
                    {
                        "time": str(e.timestamp),
                        "type": e.normalized_event_type,
                        "summary": e.summary,
                    }
                    for e in timeline_events
                ],
            )

            # Assemble Project State
            project_state = ProjectState(
                repo=repo_summary,
                session=session_summary,
                git=git_snapshot,
                recent_files=recent_files,
                analyzer=analyzer_summary,
            )

            # Return complete context
            return Context(
                context_id=str(uuid.uuid4()),
                generated_at=str(utcnow()),
                project_state=project_state,
                timeline=timeline_summary,
            )

        finally:
            db.close()
