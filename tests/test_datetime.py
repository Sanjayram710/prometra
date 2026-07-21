import pytest
import os
from datetime import datetime, timezone
from prometra.core.time import utcnow
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import AwareDateTime, SessionModel, WorkspaceModel
from prometra.tracker.session import SessionManager

@pytest.fixture
def storage():
    db_path = "/tmp/prometra_test_dt.db"
    # Ensure directory exists on Windows
    os.makedirs("/tmp", exist_ok=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass
    store = SQLiteStorage(db_path)
    yield store
    store.engine.dispose()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass

def test_utcnow_is_aware():
    now = utcnow()
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc

def test_sqlite_preserves_timezone_awareness(storage):
    db = storage.get_session()
    
    ws = WorkspaceModel(
        project_id="test_proj",
        name="Test",
        root_path="/tmp",
        created_at=utcnow(),
        updated_at=utcnow()
    )
    db.add(ws)
    
    start_time = utcnow()
    session = SessionModel(
        session_id="session1",
        project_id="test_proj",
        start_ts=start_time,
        project_path="/tmp",
        working_directory="/tmp",
        status="active"
    )
    db.add(session)
    db.commit()
    
    # Retrieve and verify
    retrieved = db.query(SessionModel).filter_by(session_id="session1").first()
    assert retrieved is not None
    assert retrieved.start_ts.tzinfo is not None
    assert retrieved.start_ts.tzinfo == timezone.utc
    
    # Calculate duration safely
    end_time = utcnow()
    duration = int((end_time - retrieved.start_ts).total_seconds())
    assert duration >= 0
    db.close()

def test_session_recovery_duration_calculation(storage):
    sm = SessionManager(storage)
    db = storage.get_session()
    
    ws = WorkspaceModel(
        project_id="test_proj",
        name="Test",
        root_path="/tmp",
        created_at=utcnow(),
        updated_at=utcnow()
    )
    db.add(ws)
    
    session = SessionModel(
        session_id="session_stale",
        project_id="test_proj",
        start_ts=utcnow(),
        project_path="/tmp",
        working_directory="/tmp",
        status="active"
    )
    db.add(session)
    db.commit()
    db.close()
    
    # This should not raise TypeError
    sm.recover_stale_sessions("test_proj")
    
    db = storage.get_session()
    recovered = db.query(SessionModel).filter_by(session_id="session_stale").first()
    assert recovered.status == "completed"
    assert recovered.duration_seconds is not None
    assert recovered.duration_seconds >= 0
    assert "Recovered stale session" in recovered.warnings
    db.close()
