import datetime
import os
import tempfile

import pytest
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.timemachine.checkpoint import CheckpointManager
from prometra.timemachine.compare import CheckpointComparer
from prometra.timemachine.models import (
    CheckpointModel,
    FileSnapshot,
)
from prometra.timemachine.restore import RestoreEngine
from prometra.timemachine.snapshot import SnapshotEngine
from prometra.timemachine.storage import CheckpointStorage
from prometra.timemachine.timeline import CheckpointTimeline
from prometra.tui.views.timemachine_view import TimeMachineView

runner = CliRunner()


@pytest.fixture
def temp_tm_env():
    orig_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, ".prometra", "prometra.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        storage = SQLiteStorage(db_path)

        # Create dummy project files
        file1 = os.path.join(tmpdir, "main.py")
        with open(file1, "w", encoding="utf-8") as f:
            f.write("print('Hello World')\n")

        file2 = os.path.join(tmpdir, "utils.py")
        with open(file2, "w", encoding="utf-8") as f:
            f.write("def add(a, b):\n    return a + b\n")

        try:
            yield tmpdir, storage
        finally:
            os.chdir(orig_cwd)
            storage.engine.dispose()


def test_checkpoint_storage(temp_tm_env):
    tmpdir, _storage = temp_tm_env
    cp_storage = CheckpointStorage(root_dir=os.path.join(tmpdir, ".prometra"))

    now = datetime.datetime.now(datetime.UTC)
    cp = CheckpointModel(
        id="chk-test-1",
        message="Test Storage Checkpoint",
        timestamp=now,
        session_id="sess-1",
        modified_files=["main.py"],
        file_hashes={"main.py": "hash123"},
    )
    snap = FileSnapshot(
        path=os.path.join(tmpdir, "main.py"),
        normalized_path="main.py",
        file_hash="hash123",
        size=20,
        content="print('Hello World')\n",
    )

    cp_storage.save_checkpoint(cp, [snap])

    loaded = cp_storage.load_checkpoint("chk-test-1")
    assert loaded is not None
    assert loaded.id == "chk-test-1"
    assert loaded.message == "Test Storage Checkpoint"

    content = cp_storage.load_file_content("chk-test-1", "main.py")
    assert content == "print('Hello World')\n"

    cps = cp_storage.list_checkpoints()
    assert len(cps) == 1
    assert cps[0].id == "chk-test-1"


def test_snapshot_engine(temp_tm_env):
    tmpdir, storage = temp_tm_env
    engine = SnapshotEngine(storage=storage, root_dir=tmpdir)

    cp, snaps = engine.capture_snapshot(message="Snapshot test")
    assert cp.id.startswith("chk-")
    assert len(snaps) >= 2
    assert "main.py" in cp.modified_files
    assert "utils.py" in cp.modified_files


def test_checkpoint_manager(temp_tm_env):
    tmpdir, storage = temp_tm_env
    mgr = CheckpointManager(storage=storage, root_dir=tmpdir)

    cp = mgr.create_checkpoint(message="Finished auth")
    assert cp.message == "Finished auth"

    fetched = mgr.get_checkpoint(cp.id)
    assert fetched is not None
    assert fetched.id == cp.id

    all_cps = mgr.list_checkpoints()
    assert len(all_cps) == 1

    search_res = mgr.search_checkpoints("auth")
    assert len(search_res) == 1
    assert search_res[0].id == cp.id


def test_restore_engine(temp_tm_env):
    tmpdir, storage = temp_tm_env
    mgr = CheckpointManager(storage=storage, root_dir=tmpdir)
    restore_eng = RestoreEngine(root_dir=tmpdir)

    # 1. Create initial checkpoint
    cp1 = mgr.create_checkpoint(message="State 1")

    # 2. Modify a file and create a new file
    file1 = os.path.join(tmpdir, "main.py")
    with open(file1, "w", encoding="utf-8") as f:
        f.write("print('Modified Hello')\n")

    file3 = os.path.join(tmpdir, "new_feature.py")
    with open(file3, "w", encoding="utf-8") as f:
        f.write("# New feature\n")

    # 3. Preview restore
    preview = restore_eng.preview_restore(cp1.id)
    assert "main.py" in preview.files_modified
    assert "new_feature.py" in preview.files_deleted

    # 4. Execute restore
    success = restore_eng.execute_restore(cp1.id)
    assert success is True

    # Verify workspace files reverted
    with open(file1, "r", encoding="utf-8") as f:
        assert f.read() == "print('Hello World')\n"
    assert not os.path.exists(file3)


def test_checkpoint_comparer(temp_tm_env):
    tmpdir, storage = temp_tm_env
    mgr = CheckpointManager(storage=storage, root_dir=tmpdir)
    comparer = CheckpointComparer(root_dir=tmpdir)

    cp1 = mgr.create_checkpoint(message="CP 1")

    # Modify file
    file1 = os.path.join(tmpdir, "main.py")
    with open(file1, "w", encoding="utf-8") as f:
        f.write("print('Hello Prometra v2.3.0')\n")

    cp2 = mgr.create_checkpoint(message="CP 2")

    diff = comparer.compare_checkpoints(cp1.id, cp2.id)
    assert diff.checkpoint_a == cp1.id
    assert diff.checkpoint_b == cp2.id
    assert "main.py" in diff.modified_files
    assert "Hello Prometra" in diff.diff_text


def test_checkpoint_timeline(temp_tm_env):
    tmpdir, storage = temp_tm_env
    mgr = CheckpointManager(storage=storage, root_dir=tmpdir)
    _cp = mgr.create_checkpoint(message="Timeline CP")

    cp_tl = CheckpointTimeline(storage=storage, root_dir=tmpdir)
    items = cp_tl.get_timeline_with_checkpoints()
    assert len(items) >= 1
    assert any(i["type"] == "checkpoint" for i in items)


def test_timemachine_tui_view(temp_tm_env):
    _tmpdir, storage = temp_tm_env
    view = TimeMachineView(storage=storage)
    view.refresh_data()
    rendered = view.render()
    assert rendered is not None


def test_cli_timemachine_commands(monkeypatch, temp_tm_env):
    tmpdir, storage = temp_tm_env
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: storage)
    monkeypatch.chdir(tmpdir)

    # 1. Create checkpoint
    res_cp = runner.invoke(app, ["checkpoint", "Initial checkpoint"])
    assert res_cp.exit_code == 0
    assert "Created Checkpoint" in res_cp.stdout

    # 2. List checkpoints
    res_list = runner.invoke(app, ["checkpoints"])
    assert res_list.exit_code == 0
    assert "Prometra Time Machine Checkpoints" in res_list.stdout

    res_json = runner.invoke(app, ["checkpoints", "--json"])
    assert res_json.exit_code == 0
    assert "Initial checkpoint" in res_json.stdout

    # 3. Timeline --checkpoints
    res_tl = runner.invoke(app, ["timeline", "--checkpoints"])
    assert res_tl.exit_code == 0
    assert "Timeline with Checkpoints" in res_tl.stdout

    # 4. Compare checkpoints
    res_cp2 = runner.invoke(app, ["checkpoint", "Second checkpoint"])
    assert res_cp2.exit_code == 0

    cps = CheckpointStorage(
        root_dir=os.path.join(tmpdir, ".prometra")
    ).list_checkpoints()
    assert len(cps) >= 2

    res_comp = runner.invoke(app, ["compare-checkpoints", cps[1].id, cps[0].id])
    assert res_comp.exit_code == 0
    assert "CHECKPOINT COMPARISON" in res_comp.stdout

    # 5. Restore checkpoint
    res_rest = runner.invoke(app, ["restore", cps[0].id, "--confirm"])
    assert res_rest.exit_code == 0
    assert "Successfully restored workspace" in res_rest.stdout
