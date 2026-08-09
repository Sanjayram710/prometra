import os
import tempfile

from prometra.core.time import utcnow
from prometra.dashboard.engine import DashboardEngine
from prometra.storage.models import SessionModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine
from prometra.tracker.filesystem import FilesystemTracker
from prometra.tracker.ignore import IgnoreManager


def test_default_ignored_directories():
    ignore_mgr = IgnoreManager()

    assert ignore_mgr.should_ignore(".venv/lib/python3.11/site-packages/pkg.py")
    assert ignore_mgr.should_ignore("venv/bin/activate")
    assert ignore_mgr.should_ignore("node_modules/express/index.js")
    assert ignore_mgr.should_ignore("__pycache__/main.cpython-311.pyc")
    assert ignore_mgr.should_ignore(".git/HEAD")
    assert ignore_mgr.should_ignore(".prometra/prometra.db")
    assert ignore_mgr.should_ignore("build/lib/main.o")
    assert ignore_mgr.should_ignore("dist/bundle.js")
    assert ignore_mgr.should_ignore(".pytest_cache/v/cache/nodeids")
    assert ignore_mgr.should_ignore(".vscode/settings.json")
    assert ignore_mgr.should_ignore(".idea/workspace.xml")


def test_default_ignored_files():
    ignore_mgr = IgnoreManager()

    assert ignore_mgr.should_ignore("app.pyc")
    assert ignore_mgr.should_ignore("debug.log")
    assert ignore_mgr.should_ignore("temp.tmp")
    assert ignore_mgr.should_ignore("Thumbs.db")
    assert ignore_mgr.should_ignore(".DS_Store")
    assert ignore_mgr.should_ignore("main.swp")

    # Meaningful files should NOT be ignored
    assert not ignore_mgr.should_ignore("main.py")
    assert not ignore_mgr.should_ignore("README.md")
    assert not ignore_mgr.should_ignore("src/auth.py")
    assert not ignore_mgr.should_ignore("frontend/App.tsx")


def test_windows_and_linux_paths():
    ignore_mgr = IgnoreManager()

    # Windows paths with backslashes
    assert ignore_mgr.should_ignore(
        r"C:\Project\.venv\Lib\site-packages\torch\__init__.py"
    )
    assert ignore_mgr.should_ignore(r"C:\Project\build\output.exe")
    assert ignore_mgr.should_ignore(r"C:\Project\app.log")
    assert not ignore_mgr.should_ignore(r"C:\Project\src\index.ts")

    # Linux paths with forward slashes
    assert ignore_mgr.should_ignore(
        "/home/user/project/.venv/lib/site-packages/numpy/__init__.py"
    )
    assert ignore_mgr.should_ignore(
        "/home/user/project/__pycache__/app.cpython-311.pyc"
    )
    assert not ignore_mgr.should_ignore("/home/user/project/src/index.ts")


def test_custom_prometraignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        ignore_file = os.path.join(tmpdir, ".prometraignore")
        with open(ignore_file, "w", encoding="utf-8") as f:
            f.write("# Custom ignore rules\n")
            f.write("\n")
            f.write("custom_output/\n")
            f.write("*.csv\n")
            f.write("secret.key\n")
            f.write("custom_output/ # Duplicate comment test\n")

        ignore_mgr = IgnoreManager(root_dir=tmpdir)

        assert ignore_mgr.should_ignore("custom_output/report.txt", root_dir=tmpdir)
        assert ignore_mgr.should_ignore("data/export.csv", root_dir=tmpdir)
        assert ignore_mgr.should_ignore("secret.key", root_dir=tmpdir)

        # Valid code file remains un-ignored
        assert not ignore_mgr.should_ignore("src/model.py", root_dir=tmpdir)


def test_nested_directories_and_globs():
    ignore_mgr = IgnoreManager()

    assert ignore_mgr.should_ignore("services/user/__pycache__/user.cpython-311.pyc")
    assert ignore_mgr.should_ignore("deeply/nested/dir/node_modules/package/index.js")
    assert ignore_mgr.should_ignore("backend/auth/.venv/pip/installer.py")


def test_filesystem_tracker_ignore_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_fs_ignore.db")
        storage = SQLiteStorage(db_path)
        try:
            engine = TimelineEngine(storage)
            ignore_mgr = IgnoreManager(root_dir=tmpdir)
            tracker = FilesystemTracker(
                watch_dir=tmpdir,
                timeline_engine=engine,
                session_id="sess-ignore-test",
                project_id="proj-ignore",
                ignore_manager=ignore_mgr,
            )

            # Queue valid file event and ignored file event
            valid_event = {
                "type": "filesystem",
                "operation": "modified",
                "path": os.path.join(tmpdir, "main.py"),
                "normalized_relative_path": "main.py",
                "timestamp": utcnow(),
            }
            ignored_event = {
                "type": "filesystem",
                "operation": "modified",
                "path": os.path.join(tmpdir, ".venv", "lib", "site-packages", "pkg.py"),
                "normalized_relative_path": ".venv/lib/site-packages/pkg.py",
                "timestamp": utcnow(),
            }

            tracker._queue_event(valid_event)
            tracker._queue_event(ignored_event)
            tracker._flush()

            # Query stored timeline events
            db = storage.get_session()
            from prometra.storage.models import TimelineEventModel

            events = db.query(TimelineEventModel).all()
            db.close()

            assert len(events) == 1
            assert events[0].summary == "File modified: main.py"
        finally:
            storage.engine.dispose()


def test_dashboard_excludes_ignored_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_dash_ignore.db")
        storage = SQLiteStorage(db_path)
        try:
            engine = TimelineEngine(storage)
            ignore_mgr = IgnoreManager(root_dir=tmpdir)
            tracker = FilesystemTracker(
                watch_dir=tmpdir,
                timeline_engine=engine,
                session_id="sess-dash-ignore",
                project_id="proj-dash",
                ignore_manager=ignore_mgr,
            )

            # Create session model
            db = storage.get_session()
            now = utcnow()
            sess = SessionModel(
                session_id="sess-dash-ignore",
                project_id="proj-dash",
                start_ts=now,
                end_ts=now,
                duration_seconds=300,
                project_path=tmpdir,
                working_directory=tmpdir,
                status="completed",
            )
            db.add(sess)
            db.commit()
            db.close()

            tracker._queue_event(
                {
                    "type": "filesystem",
                    "operation": "modified",
                    "path": os.path.join(tmpdir, "app.py"),
                    "normalized_relative_path": "app.py",
                    "timestamp": now,
                }
            )
            tracker._flush()

            dash_engine = DashboardEngine(storage)
            metrics = dash_engine.compute_metrics()

            # Ensure top edited files only contains app.py and no .venv or node_modules
            file_paths = [f.path for f in metrics.filesystem.top_edited_files]
            assert "app.py" in file_paths
            assert not any(
                ".venv" in p or "node_modules" in p or "__pycache__" in p
                for p in file_paths
            )
        finally:
            storage.engine.dispose()
