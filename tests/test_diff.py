import pytest
import os
import json
import tempfile
import datetime
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, AiEventModel, SessionModel
from prometra.timeline.engine import TimelineEngine
from prometra.diff.engine import DiffEngine
from prometra.diff.models import FileVersion, DiffResult
from prometra.diff.formatter import DiffFormatter
from prometra.diff.exporter import DiffExporter
from prometra.core.time import utcnow

runner = CliRunner()

@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_diff.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()

@pytest.fixture
def populated_diff_db(temp_storage):
    db = temp_storage.get_session()
    
    # Session 1
    s1 = SessionModel(
        session_id="sess-1",
        project_id="test_proj",
        start_ts=utcnow() - datetime.timedelta(hours=2),
        duration_seconds=3600,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s1)
    
    # Session 2
    s2 = SessionModel(
        session_id="sess-2",
        project_id="test_proj",
        start_ts=utcnow() - datetime.timedelta(hours=1),
        duration_seconds=1800,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s2)
    db.commit()

    # Timeline event 1 (Session 1, Event 1)
    tl1 = TimelineEventModel(
        normalized_event_type="filesystem",
        timestamp=utcnow() - datetime.timedelta(hours=2),
        sequence=1,
        source="filesystem",
        session_id="sess-1",
        related_event_ids=["fs-1"],
        summary="File modified: hello.py"
    )
    db.add(tl1)

    ai1 = AiEventModel(
        event_id="fs-1",
        session_id="sess-1",
        timestamp=utcnow() - datetime.timedelta(hours=2),
        event_type="FileModified",
        connector="filesystem",
        description="Modified hello.py",
        extra_metadata={"path": "hello.py", "content": 'print("Hello")\n'}
    )
    db.add(ai1)

    # Timeline event 2 (Session 1, Event 2)
    tl2 = TimelineEventModel(
        normalized_event_type="filesystem",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=45),
        sequence=2,
        source="filesystem",
        session_id="sess-1",
        related_event_ids=["fs-2"],
        summary="File modified: hello.py"
    )
    db.add(tl2)

    ai2 = AiEventModel(
        event_id="fs-2",
        session_id="sess-1",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=45),
        event_type="FileModified",
        connector="filesystem",
        description="Modified hello.py",
        extra_metadata={"path": "hello.py", "content": 'print("Hello World")\nprint("Welcome")\n'}
    )
    db.add(ai2)

    # Timeline event 3 (Session 2, Event 3)
    tl3 = TimelineEventModel(
        normalized_event_type="filesystem",
        timestamp=utcnow() - datetime.timedelta(minutes=30),
        sequence=3,
        source="filesystem",
        session_id="sess-2",
        related_event_ids=["fs-3"],
        summary="File modified: hello.py"
    )
    db.add(tl3)

    ai3 = AiEventModel(
        event_id="fs-3",
        session_id="sess-2",
        timestamp=utcnow() - datetime.timedelta(minutes=30),
        event_type="FileModified",
        connector="filesystem",
        description="Modified hello.py",
        extra_metadata={"path": "hello.py", "content": 'print("Hello World!")\nprint("Welcome to Prometra")\n'}
    )
    db.add(ai3)

    db.commit()
    db.close()
    return temp_storage

def test_basic_diff(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    # Diff between default latest pair or explicit events 1 & 2
    res = engine.compute_diff("hello.py", from_event=1, to_event=2)
    assert res.file == "hello.py"
    assert res.event_from == 1
    assert res.event_to == 2
    assert res.modified_lines == 1
    assert res.added_lines == 1
    assert res.removed_lines == 0
    assert '-print("Hello")' in res.diff or '- print("Hello")' in res.diff or 'Hello' in res.diff

def test_identical_versions(temp_storage):
    db = temp_storage.get_session()
    tl1 = TimelineEventModel(
        normalized_event_type="filesystem",
        timestamp=utcnow() - datetime.timedelta(hours=1),
        sequence=1,
        source="filesystem",
        session_id="sess-1",
        related_event_ids=["fs-identical-1"],
        summary="File modified: same.py"
    )
    tl2 = TimelineEventModel(
        normalized_event_type="filesystem",
        timestamp=utcnow() - datetime.timedelta(minutes=30),
        sequence=2,
        source="filesystem",
        session_id="sess-1",
        related_event_ids=["fs-identical-2"],
        summary="File modified: same.py"
    )
    ai1 = AiEventModel(
        event_id="fs-identical-1",
        session_id="sess-1",
        timestamp=utcnow() - datetime.timedelta(hours=1),
        event_type="FileModified",
        connector="filesystem",
        extra_metadata={"path": "same.py", "content": "same content\n"}
    )
    ai2 = AiEventModel(
        event_id="fs-identical-2",
        session_id="sess-1",
        timestamp=utcnow() - datetime.timedelta(minutes=30),
        event_type="FileModified",
        connector="filesystem",
        extra_metadata={"path": "same.py", "content": "same content\n"}
    )
    db.add_all([tl1, tl2, ai1, ai2])
    db.commit()
    db.close()

    engine = DiffEngine(temp_storage)
    res = engine.compute_diff("same.py", from_event=1, to_event=2)
    assert res.added_lines == 0
    assert res.removed_lines == 0
    assert res.modified_lines == 0
    assert res.diff == ""

def test_multiple_versions(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    res_1_3 = engine.compute_diff("hello.py", from_event=1, to_event=3)
    assert res_1_3.event_from == 1
    assert res_1_3.event_to == 3

    res_2_3 = engine.compute_diff("hello.py", from_event=2, to_event=3)
    assert res_2_3.event_from == 2
    assert res_2_3.event_to == 3

def test_session_filter(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    res = engine.compute_diff("hello.py", session_id="sess-1")
    assert res.session_id == "sess-1"
    assert res.event_from == 1
    assert res.event_to == 2

def test_event_filter(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    res = engine.compute_diff("hello.py", from_event=1, to_event=2)
    assert res.event_from == 1
    assert res.event_to == 2

def test_markdown_export(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    res = engine.compute_diff("hello.py", from_event=1, to_event=2)
    md = DiffExporter.to_markdown(res)
    assert "# File Diff" in md
    assert "**File:** `hello.py`" in md
    assert "```diff" in md

def test_json_export(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    res = engine.compute_diff("hello.py", from_event=1, to_event=2)
    json_str = DiffExporter.to_json(res)
    data = json.loads(json_str)
    assert data["file"] == "hello.py"
    assert data["event_from"] == 1
    assert data["event_to"] == 2
    assert "added_lines" in data
    assert "removed_lines" in data
    assert "modified_lines" in data
    assert "diff" in data

def test_invalid_file(temp_storage):
    engine = DiffEngine(temp_storage)
    with pytest.raises(ValueError) as excinfo:
        engine.compute_diff("nonexistent_file_xyz.py")
    assert "not found" in str(excinfo.value)

def test_missing_event(populated_diff_db):
    engine = DiffEngine(populated_diff_db)
    with pytest.raises(ValueError) as excinfo:
        engine.compute_diff("hello.py", from_event=999, to_event=2)
    assert "Event 999 not found" in str(excinfo.value)

def test_no_history(temp_storage):
    engine = DiffEngine(temp_storage)
    with pytest.raises(ValueError) as excinfo:
        engine.compute_diff("empty_history.py")
    assert "not found" in str(excinfo.value) or "No event history" in str(excinfo.value)

def test_cli_diff(monkeypatch, populated_diff_db):
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: populated_diff_db)

    res_help = runner.invoke(app, ["diff", "--help"])
    assert res_help.exit_code == 0
    assert "Inspect changes between tracked file versions" in res_help.stdout or "FILE_PATH" in res_help.stdout

    res_json = runner.invoke(app, ["diff", "hello.py", "--from-event", "1", "--to-event", "2", "--json"])
    assert res_json.exit_code == 0
    assert '"file": "hello.py"' in res_json.stdout

    res_md = runner.invoke(app, ["diff", "hello.py", "--from-event", "1", "--to-event", "2", "--markdown"])
    assert res_md.exit_code == 0
    assert "# File Diff" in res_md.stdout

    res_plain = runner.invoke(app, ["diff", "hello.py", "--from-event", "1", "--to-event", "2"])
    assert res_plain.exit_code == 0
    assert "hello.py" in res_plain.stdout
