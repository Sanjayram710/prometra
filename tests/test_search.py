import pytest
import os
import tempfile
import datetime
from typer.testing import CliRunner
from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.search.engine import SearchEngine
from prometra.search.formatter import SearchFormatter
from prometra.search.exporter import SearchExporter
from prometra.storage.models import SessionModel
from prometra.core.time import utcnow

runner = CliRunner()

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_search.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()

@pytest.fixture
def populated_search_engine(temp_db):
    engine = TimelineEngine(temp_db)
    now = utcnow()
    
    # Create Session 1
    db = temp_db.get_session()
    s1 = SessionModel(
        session_id="sess-search-100",
        project_id="test_project",
        start_ts=now - datetime.timedelta(hours=2),
        end_ts=now,
        duration_seconds=7200,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s1)
    db.commit()
    db.close()
    
    # Timeline Events
    engine.append_event({
        "type": "session",
        "session_id": "sess-search-100",
        "timestamp": now - datetime.timedelta(hours=2),
        "source": "system",
        "summary": "Session Started"
    })
    engine.append_event({
        "type": "filesystem",
        "session_id": "sess-search-100",
        "timestamp": now - datetime.timedelta(hours=1, minutes=50),
        "source": "filesystem",
        "summary": "File created: hello.py"
    })
    engine.append_event({
        "type": "filesystem",
        "session_id": "sess-search-100",
        "timestamp": now - datetime.timedelta(hours=1, minutes=40),
        "source": "filesystem",
        "summary": "File modified: backend/auth.py (JWT authentication)"
    })
    engine.append_event({
        "type": "git",
        "session_id": "sess-search-100",
        "timestamp": now - datetime.timedelta(hours=1, minutes=30),
        "source": "git",
        "summary": "Git Commit ffe399c: feat(auth): add authentication middleware"
    })
    engine.append_event({
        "type": "PromptSubmitted",
        "session_id": "sess-search-100",
        "timestamp": now - datetime.timedelta(hours=1),
        "source": "claude",
        "actor_tool": "claude",
        "summary": "Prompt Submitted: Implement JWT token verification"
    })
    engine.append_event({
        "type": "ResponseReceived",
        "session_id": "sess-search-100",
        "timestamp": now - datetime.timedelta(minutes=30),
        "source": "claude",
        "actor_tool": "claude",
        "summary": "Response Received: Updated authentication logic"
    })
    
    return SearchEngine(temp_db)

def test_simple_keyword_search(populated_search_engine):
    res = populated_search_engine.search_events("hello.py")
    assert res.total_results == 1
    assert "hello.py" in res.results[0].summary

    res_auth = populated_search_engine.search_events("authentication")
    assert res_auth.total_results >= 2

def test_case_insensitive_search(populated_search_engine):
    res_upper = populated_search_engine.search_events("HELLO.PY")
    assert res_upper.total_results == 1

    res_mixed = populated_search_engine.search_events("JwT")
    assert res_mixed.total_results == 2

def test_category_filters(populated_search_engine):
    res_fs = populated_search_engine.search_events("file", category="filesystem")
    assert res_fs.total_results == 2

    res_git = populated_search_engine.search_events("auth", category="git")
    assert res_git.total_results == 1
    assert "Git Commit" in res_git.results[0].summary

    res_ai = populated_search_engine.search_events("JWT", category="ai")
    assert res_ai.total_results >= 1
    assert "claude" in res_ai.results[0].source

def test_session_filter(populated_search_engine):
    res = populated_search_engine.search_events("hello", session="sess-search-100")
    assert res.total_results == 1

    res_invalid = populated_search_engine.search_events("hello", session="sess-non-existent")
    assert res_invalid.total_results == 0

def test_date_range_filters(populated_search_engine):
    res_today = populated_search_engine.search_events("auth", today=True)
    assert res_today.total_results >= 1

    res_week = populated_search_engine.search_events("auth", week=True)
    assert res_week.total_results >= 1

    now = utcnow()
    since_str = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    until_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    res_range = populated_search_engine.search_events("auth", since=since_str, until=until_str)
    assert res_range.total_results >= 1

def test_limit_filter(populated_search_engine):
    res = populated_search_engine.search_events("auth", limit=1)
    assert res.total_results == 1

def test_invalid_date_and_session_handling(populated_search_engine):
    # Invalid date strings should degrade gracefully to None date filters without crashing
    res_bad_date = populated_search_engine.search_events("auth", since="not-a-valid-date", until="invalid-until")
    assert res_bad_date.total_results >= 1

    # Non-existent session ID should return 0 results
    res_bad_sess = populated_search_engine.search_events("auth", session="sess-invalid-999999")
    assert res_bad_sess.total_results == 0

def test_no_results_and_unicode_search(populated_search_engine):
    res_none = populated_search_engine.search_events("non_existent_keyword_xyz_123")
    assert res_none.total_results == 0

    res_unicode = populated_search_engine.search_events("tést_üñícôdê")
    assert res_unicode.total_results == 0

def test_sql_injection_prevention(populated_search_engine):
    # Attempt SQL injection attack strings
    injection_strings = [
        "' OR '1'='1",
        "'; DROP TABLE timeline_events; --",
        "\" OR 1=1 --",
        "%_SELECT * FROM sessions;%"
    ]
    for inj in injection_strings:
        res = populated_search_engine.search_events(inj)
        # Should execute safely without raising exception or destroying tables
        assert res.total_results == 0

def test_search_formatter(populated_search_engine):
    res = populated_search_engine.search_events("authentication")
    
    json_out = SearchFormatter.to_json(res)
    assert '"total_results":' in json_out
    assert "authentication" in json_out

    md_out = SearchFormatter.to_markdown(res)
    assert "# Prometra Search Results" in md_out
    assert "authentication" in md_out

def test_search_exporter(populated_search_engine):
    res = populated_search_engine.search_events("authentication")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = os.path.join(tmpdir, "search.md")
        json_path = os.path.join(tmpdir, "search.json")
        
        SearchExporter.export(res, md_path)
        assert os.path.exists(md_path)
        with open(md_path, "r", encoding="utf-8") as f:
            assert "# Prometra Search Results" in f.read()

        SearchExporter.export(res, json_path)
        assert os.path.exists(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            assert '"query":' in f.read()

def test_cli_search_command(monkeypatch, populated_search_engine):
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: populated_search_engine.storage)
    
    # Test CLI search
    res_cli = runner.invoke(app, ["search", "hello.py"])
    assert res_cli.exit_code == 0
    assert "hello.py" in res_cli.stdout

    # Test CLI search with --type
    res_type = runner.invoke(app, ["search", "auth", "--type", "git"])
    assert res_type.exit_code == 0

    # Test CLI search with --json
    res_json = runner.invoke(app, ["search", "auth", "--json"])
    assert res_json.exit_code == 0
    assert '"query": "auth"' in res_json.stdout

    # Test CLI search with --markdown
    res_md = runner.invoke(app, ["search", "auth", "--markdown"])
    assert res_md.exit_code == 0
    assert "# Prometra Search Results" in res_md.stdout

def test_large_dataset_performance_sanity_check(temp_db):
    engine = TimelineEngine(temp_db)
    now = utcnow()
    
    # Generate batch timeline events
    events = []
    for i in range(500):
        engine.append_event({
            "type": "filesystem",
            "session_id": "sess-perf-test",
            "timestamp": now - datetime.timedelta(seconds=i),
            "source": "filesystem",
            "summary": f"File modified: src/module_{i}.py (performance test record)"
        })
        
    search_eng = SearchEngine(temp_db)
    res = search_eng.search_events("module_250")
    
    assert res.total_results == 1
    assert res.execution_time_ms < 150.0 # Latency target <150 ms
