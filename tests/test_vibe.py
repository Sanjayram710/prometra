import os
import shutil
import tempfile
import pytest
from typer.testing import CliRunner

from prometra.ai.vibe import ModelOrchestrator, VibeEngine
from prometra.cli.main import app
from prometra.connectors.events import EventBus
from prometra.connectors.gemini.connector import GeminiConnector, GeminiQuotaExceededError
from prometra.connectors.gpt.connector import GPTConnector, GPTQuotaExceededError
from prometra.storage.models import AiEventModel, FilesystemEventModel, TimelineEventModel
from prometra.storage.sqlite import SQLiteStorage
from prometra.timeline.engine import TimelineEngine


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def storage(temp_dir):
    db_path = os.path.join(temp_dir, ".prometra", "prometra.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    s = SQLiteStorage(db_path)
    yield s
    s.engine.dispose()


def test_gemini_connector():
    conn = GeminiConnector()
    conn.connect()
    assert conn.health().state == "connected"

    res = conn.generate("Test Gemini Prompt")
    assert res["provider"] == "gemini"
    assert "gemini" in res["model"]
    assert "Interpretation" in res["content"] or len(res["content"]) > 0

    with pytest.raises(GeminiQuotaExceededError):
        conn.generate("Prompt", trigger_limit=True)


def test_gpt_connector():
    conn = GPTConnector()
    conn.connect()
    assert conn.health().state == "connected"

    res = conn.generate("Test GPT Prompt")
    assert res["provider"] == "gpt"
    assert "gpt" in res["model"]

    with pytest.raises(GPTQuotaExceededError):
        conn.generate("Prompt", trigger_limit=True)


def test_model_orchestrator_primary_success():
    bus = EventBus()
    orchestrator = ModelOrchestrator(event_bus=bus)

    events = []
    bus.subscribe("*", lambda e: events.append(e))

    res = orchestrator.execute_prompt(
        prompt="Write a test function",
        primary_model="gemini",
        fallback_models=["claude", "gpt"],
    )

    assert res["success"] is True
    assert res["provider"] == "gemini"
    assert res["fallback_occurred"] is False
    assert len(events) >= 2


def test_model_orchestrator_quota_fallback():
    bus = EventBus()
    orchestrator = ModelOrchestrator(event_bus=bus)

    events = []
    bus.subscribe("*", lambda e: events.append(e))

    # Trigger quota limit on Gemini to force fallback to Claude/GPT
    res = orchestrator.execute_prompt(
        prompt="Build login feature",
        primary_model="gemini",
        fallback_models=["claude", "gpt"],
        trigger_limit_for="gemini",
    )

    assert res["success"] is True
    assert res["provider"] in ["claude", "gpt"]
    assert res["fallback_occurred"] is True
    assert "gemini" in res["attempted"]

    event_types = [e.event_type for e in events]
    assert "RetryAttempt" in event_types
    assert "ModelChanged" in event_types


def test_vibe_engine_file_diffs_and_persistence(temp_dir, storage):
    bus = EventBus()
    timeline_engine = TimelineEngine(storage, event_bus=bus)
    engine = VibeEngine(storage, event_bus=bus)

    def sample_code_action(dir_path):
        new_file = os.path.join(dir_path, "auth.py")
        with open(new_file, "w", encoding="utf-8") as f:
            f.write("def login(user, password):\n    return True\n")

    res = engine.run_vibe_prompt(
        prompt="Implement authentication module",
        workspace_dir=temp_dir,
        primary_model="gemini",
        fallback_models=["claude", "gpt"],
        code_action=sample_code_action,
    )

    assert res["file_diffs"]["total_files_changed"] > 0
    assert len(res["file_diffs"]["created"]) == 1
    assert res["file_diffs"]["created"][0]["file"] == "auth.py"

    # Verify DB persistence
    db = storage.get_session()
    ai_events = db.query(AiEventModel).all()
    fs_events = db.query(FilesystemEventModel).all()
    tl_events = db.query(TimelineEventModel).all()
    db.close()

    assert len(ai_events) > 0
    assert len(fs_events) > 0
    assert len(tl_events) > 0


def test_cli_vibe_command(temp_dir):
    runner = CliRunner()
    old_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        # Init project
        init_res = runner.invoke(app, ["init"])
        assert init_res.exit_code == 0

        # Run vibe command
        vibe_res = runner.invoke(
            app,
            [
                "vibe",
                "-p",
                "Create user.py model",
                "--primary-model",
                "gemini",
                "--fallback-models",
                "claude,gpt",
            ],
        )
        assert vibe_res.exit_code == 0
        assert "PROMETRA VIBE CODING TERMINAL" in vibe_res.output
        assert "GEMINI" in vibe_res.output
    finally:
        os.chdir(old_cwd)
