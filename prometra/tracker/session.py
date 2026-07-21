import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from prometra.core.schemas import Session, Workspace
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import SessionModel, WorkspaceModel

def utcnow():
    return datetime.now(timezone.utc)

class SessionManager:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def start_session(self, project_id: str, project_path: str, working_directory: str) -> Session:
        db = self.storage.get_session()
        try:
            active = db.query(SessionModel).filter_by(project_id=project_id, status="active").first()
            if active:
                # Mock returning existing
                pass
            
            session_id = str(uuid.uuid4())
            new_session = Session(
                session_id=session_id,
                project_id=project_id,
                project_path=project_path,
                working_directory=working_directory
            )
            
            ws = db.query(WorkspaceModel).filter_by(project_id=project_id).first()
            if not ws:
                ws_model = WorkspaceModel(
                    project_id=project_id,
                    name=os.path.basename(project_path),
                    root_path=project_path,
                    created_at=utcnow(),
                    updated_at=utcnow(),
                    status="active"
                )
                db.add(ws_model)

            session_model = SessionModel(
                session_id=new_session.session_id,
                project_id=new_session.project_id,
                start_ts=new_session.start_ts,
                project_path=new_session.project_path,
                working_directory=new_session.working_directory,
                status=new_session.status
            )
            db.add(session_model)
            db.commit()
            return new_session
        finally:
            db.close()

    def end_session(self, session_id: str):
        db = self.storage.get_session()
        try:
            session = db.query(SessionModel).filter_by(session_id=session_id).first()
            if session:
                session.end_ts = utcnow()
                session.duration_seconds = int((session.end_ts - session.start_ts).total_seconds())
                session.status = "completed"
                db.commit()
        finally:
            db.close()
