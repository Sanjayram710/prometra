import os
import tempfile

import pytest
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.plugins.base import BasePlugin
from prometra.plugins.examples import HelloPlugin, SlackNotifier, StatisticsPlugin
from prometra.plugins.exceptions import (
    DuplicatePluginError,
)
from prometra.plugins.loader import PluginLoader
from prometra.plugins.manager import PluginManager
from prometra.plugins.registry import PluginRegistry

runner = CliRunner()


class CustomTestPlugin(BasePlugin):
    name = "CustomTestPlugin"
    version = "1.2.3"
    author = "Tester"
    description = "Custom test plugin."

    def __init__(self, config=None):
        super().__init__(config)
        self.initialized = False
        self.shutdown_called = False
        self.session_events = []
        self.file_events = []

    def initialize(self, context=None):
        self.initialized = True

    def shutdown(self):
        self.shutdown_called = True

    def on_session_started(self, session_data):
        self.session_events.append("started")

    def on_file_changed(self, event_data):
        self.file_events.append(event_data.get("path"))


class FaultyPlugin(BasePlugin):
    name = "FaultyPlugin"
    version = "0.0.1"
    description = "Plugin that raises exceptions."

    def on_file_changed(self, event_data):
        raise RuntimeError("Intentional plugin error during hook execution!")


def test_base_plugin_defaults():
    p = BasePlugin()
    assert p.name == "BasePlugin"
    assert p.version == "0.1.0"
    assert p.enabled is True
    meta = p.metadata()
    assert meta["name"] == "BasePlugin"


def test_registry_registration():
    reg = PluginRegistry(register_defaults=False)
    reg.register(CustomTestPlugin)
    assert "CustomTestPlugin" in reg.list_names()
    assert reg.get("CustomTestPlugin") is CustomTestPlugin

    with pytest.raises(DuplicatePluginError):
        reg.register(CustomTestPlugin, overwrite=False)

    reg.register(CustomTestPlugin, overwrite=True)
    assert reg.get("CustomTestPlugin") is CustomTestPlugin

    reg.unregister("CustomTestPlugin")
    assert "CustomTestPlugin" not in reg.list_names()


def test_registry_invalid_subclass():
    reg = PluginRegistry(register_defaults=False)

    class NotAPlugin:
        pass

    with pytest.raises((TypeError, ValueError)):
        reg.register(NotAPlugin)


def test_loader_discovery_from_temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_code = """
from prometra.plugins.base import BasePlugin

class DynamicFilePlugin(BasePlugin):
    name = "DynamicFilePlugin"
    version = "2.0.0"
    description = "Dynamically loaded from directory"
"""
        plugin_path = os.path.join(tmpdir, "my_plugin.py")
        with open(plugin_path, "w", encoding="utf-8") as f:
            f.write(plugin_code)

        reg = PluginRegistry(register_defaults=False)
        loader = PluginLoader(registry=reg, search_paths=[tmpdir])
        loaded = loader.discover_and_load()

        assert len(loaded) == 1
        assert loaded[0].name == "DynamicFilePlugin"
        assert reg.get("DynamicFilePlugin") is not None


def test_loader_invalid_file_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        broken_code = "def invalid_syntax(:"
        broken_path = os.path.join(tmpdir, "broken.py")
        with open(broken_path, "w", encoding="utf-8") as f:
            f.write(broken_code)

        reg = PluginRegistry(register_defaults=False)
        loader = PluginLoader(registry=reg, search_paths=[tmpdir])
        loaded = loader.discover_and_load()

        assert len(loaded) == 0
        assert broken_path in loader.load_errors


def test_manager_lifecycle_and_hooks():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "plugins.json")
        reg = PluginRegistry(register_defaults=False)
        reg.register(CustomTestPlugin)

        pm = PluginManager(registry=reg, config_path=config_path, search_paths=[])
        active = pm.load_plugins()

        assert "CustomTestPlugin" in active
        instance = active["CustomTestPlugin"]
        assert instance.initialized is True

        pm.trigger_hook("on_session_started", {"session_id": "s1"})
        assert instance.session_events == ["started"]

        pm.trigger_hook("on_file_changed", {"path": "main.py"})
        assert instance.file_events == ["main.py"]

        pm.disable_plugin("CustomTestPlugin")
        assert "CustomTestPlugin" not in pm.active_plugins
        assert instance.shutdown_called is True

        pm.enable_plugin("CustomTestPlugin")
        assert "CustomTestPlugin" in pm.active_plugins


def test_manager_fault_isolation():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "plugins.json")
        reg = PluginRegistry(register_defaults=False)
        reg.register(CustomTestPlugin)
        reg.register(FaultyPlugin)

        pm = PluginManager(registry=reg, config_path=config_path, search_paths=[])
        pm.load_plugins()

        # Trigger hook: FaultyPlugin should raise exception, get caught, auto-disabled, while CustomTestPlugin succeeds
        results = pm.trigger_hook("on_file_changed", {"path": "test.py"})

        assert "CustomTestPlugin" in results
        assert "FaultyPlugin" not in pm.active_plugins
        assert "FaultyPlugin" in pm.disabled_names


def test_builtin_example_plugins():
    hello = HelloPlugin()
    hello.initialize()
    hello.on_session_started({"session_id": "sess-1"})
    hello.on_session_ended({"session_id": "sess-1"})
    assert len(hello.logs) == 3

    slack = SlackNotifier(config={"webhook_url": "https://slack.mock"})
    slack.on_session_started({"session_id": "sess-1"})
    slack.on_file_changed({"path": "app.py"})
    assert len(slack.notifications) == 2

    stats = StatisticsPlugin()
    stats.on_file_changed({"path": "a.py"})
    stats.on_file_changed({"path": "b.py"})
    assert stats.file_change_count == 2
    assert len(stats.changed_files) == 2


def test_cli_plugins_commands(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "plugins.json")
        reg = PluginRegistry(register_defaults=True)
        pm = PluginManager(registry=reg, config_path=config_path, search_paths=[])
        pm.load_plugins()

        monkeypatch.setattr("prometra.cli.plugins_cmd.get_manager", lambda: pm)

        # 1. prometra plugins / list
        res_list = runner.invoke(app, ["plugins"])
        assert res_list.exit_code == 0
        assert "HelloPlugin" in res_list.stdout

        # 2. prometra plugins disable HelloPlugin
        res_dis = runner.invoke(app, ["plugins", "disable", "HelloPlugin"])
        assert res_dis.exit_code == 0
        assert "Disabled plugin 'HelloPlugin'" in res_dis.stdout

        # 3. prometra plugins enable HelloPlugin
        res_en = runner.invoke(app, ["plugins", "enable", "HelloPlugin"])
        assert res_en.exit_code == 0
        assert "Enabled plugin 'HelloPlugin'" in res_en.stdout

        # 4. prometra plugins reload
        res_rel = runner.invoke(app, ["plugins", "reload"])
        assert res_rel.exit_code == 0
        assert "Reloaded plugins successfully" in res_rel.stdout

        # 5. enable nonexistent
        res_err = runner.invoke(app, ["plugins", "enable", "NonExistentPlugin"])
        assert res_err.exit_code == 0
        assert "Error:" in res_err.stdout
