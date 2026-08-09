import contextlib
import os
import uuid

from prometra.core.schemas import Session
from prometra.core.time import utcnow
from prometra.storage.models import SessionModel, WorkspaceModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine


class SessionManager:
    def __init__(
        self, storage: SQLiteStorage, timeline_engine: TimelineEngine | None = None
    ):
        self.storage = storage
        self.timeline_engine = timeline_engine or TimelineEngine(storage)

    def recover_stale_sessions(self, project_id: str):
        db = self.storage.get_session()
        try:
            active_sessions = (
                db.query(SessionModel)
                .filter_by(project_id=project_id, status="active")
                .all()
            )
            for s in active_sessions:
                s.status = "completed"
                s.end_ts = utcnow()
                s.duration_seconds = int((s.end_ts - s.start_ts).total_seconds())
                warnings = s.warnings or []
                if "Recovered stale session" not in warnings:
                    warnings.append("Recovered stale session")
                s.warnings = warnings
            db.commit()
        finally:
            db.close()

    def start_session(
        self,
        project_id: str,
        project_path: str,
        working_directory: str,
        config_snapshot: dict | None = None,
    ) -> Session:
        self.recover_stale_sessions(project_id)
        db = self.storage.get_session()
        try:
            session_id = str(uuid.uuid4())
            new_session = Session(
                session_id=session_id,
                project_id=project_id,
                project_path=project_path,
                working_directory=working_directory,
                config_snapshot=config_snapshot or {},
            )

            ws = db.query(WorkspaceModel).filter_by(project_id=project_id).first()
            if not ws:
                ws_model = WorkspaceModel(
                    project_id=project_id,
                    name=os.path.basename(project_path),
                    root_path=project_path,
                    created_at=utcnow(),
                    updated_at=utcnow(),
                    status="active",
                )
                db.add(ws_model)

            session_model = SessionModel(
                session_id=new_session.session_id,
                project_id=new_session.project_id,
                start_ts=new_session.start_ts,
                project_path=new_session.project_path,
                working_directory=new_session.working_directory,
                status=new_session.status,
                config_snapshot=new_session.config_snapshot,
            )
            db.add(session_model)
            db.commit()

            # Record Session Started event in timeline_events
            with contextlib.suppress(Exception):
                self.timeline_engine.append_event(
                    {
                        "type": "session",
                        "session_id": session_id,
                        "source": "system",
                        "summary": "Session Started",
                    }
                )

            return new_session
        finally:
            db.close()

    def end_session(self, session_id: str):
        db = self.storage.get_session()
        try:
            session = db.query(SessionModel).filter_by(session_id=session_id).first()
            if session:
                session.end_ts = utcnow()
                session.duration_seconds = int(
                    (session.end_ts - session.start_ts).total_seconds()
                )
                session.status = "completed"
                db.commit()

                # Record Session Ended event in timeline_events
                with contextlib.suppress(Exception):
                    self.timeline_engine.append_event(
                        {
                            "type": "session",
                            "session_id": session_id,
                            "source": "system",
                            "summary": "Session Ended",
                        }
                    )
        finally:
            db.close()
