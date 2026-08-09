import json
import logging
import os
from typing import Any

from prometra.plugins.base import BasePlugin
from prometra.plugins.exceptions import PluginNotFoundError
from prometra.plugins.loader import PluginLoader
from prometra.plugins.registry import PluginRegistry

logger = logging.getLogger("prometra.plugins")


class PluginManager:
    """Manages plugin discovery, configuration persistence, lifecycle, and safe fault-isolated event dispatching."""

    def __init__(
        self,
        registry: PluginRegistry | None = None,
        config_path: str | None = None,
        search_paths: list[str] | None = None,
    ):
        self.registry = registry or PluginRegistry()
        self.loader = PluginLoader(registry=self.registry, search_paths=search_paths)
        self.config_path = config_path or self._default_config_path()

        self.active_plugins: dict[str, BasePlugin] = {}
        self.enabled_names: list[str] = []
        self.disabled_names: list[str] = []
        self.plugin_configs: dict[str, dict[str, Any]] = {}
        self.execution_errors: dict[str, list[str]] = {}

    @staticmethod
    def _default_config_path() -> str:
        user_dir = os.path.expanduser("~/.prometra")
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, "plugins.json")

    def load_config(self) -> dict[str, Any]:
        """Load plugin status and options from plugins.json configuration file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"Failed to read plugins config from {self.config_path}: {e}"
                )
        return {"enabled": [], "disabled": [], "config": {}}

    def save_config(self) -> None:
        """Persist current enabled/disabled state and plugin configurations to plugins.json."""
        data = {
            "enabled": self.enabled_names,
            "disabled": self.disabled_names,
            "config": self.plugin_configs,
        }
        dir_name = os.path.dirname(self.config_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_plugins(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, BasePlugin]:
        """Discover, instantiate, and initialize enabled plugins."""
        # 1. Dynamic discovery
        self.loader.discover_and_load()

        # 2. Read config
        cfg = self.load_config()
        configured_disabled = cfg.get("disabled", [])
        self.plugin_configs = cfg.get("config", {})

        all_registered = self.registry.list_names()

        # Determine enabled plugins: if plugins.json lists explicitly, use it; otherwise default to registered
        for name in all_registered:
            if name in configured_disabled:
                if name not in self.disabled_names:
                    self.disabled_names.append(name)
            else:
                if name not in self.enabled_names:
                    self.enabled_names.append(name)

        # 3. Instantiate and initialize enabled plugins
        for name in self.enabled_names:
            if name in self.active_plugins:
                continue

            plugin_cls = self.registry.get(name)
            if not plugin_cls:
                continue

            p_config = self.plugin_configs.get(name, {})
            try:
                instance = plugin_cls(config=p_config)
                instance.initialize(context=context)
                self.active_plugins[name] = instance
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to initialize plugin '{name}': {e}")
                self.disable_plugin(name, reason=str(e))

        return self.active_plugins

    def reload_plugins(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, BasePlugin]:
        """Shutdown existing plugins, reload discovery, and re-initialize."""
        self.shutdown_plugins()
        self.active_plugins.clear()
        self.enabled_names.clear()
        self.disabled_names.clear()
        return self.load_plugins(context=context)

    def shutdown_plugins(self) -> None:
        """Gracefully shut down all active plugins."""
        for name, plugin in list(self.active_plugins.items()):
            try:
                plugin.shutdown()
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error shutting down plugin '{name}': {e}")
        self.active_plugins.clear()

    def enable_plugin(
        self, name: str, context: dict[str, Any] | None = None
    ) -> None:
        """Enable a plugin by name and save configuration."""
        plugin_cls = self.registry.get(name)
        if not plugin_cls:
            raise PluginNotFoundError(f"Plugin '{name}' not found in registry.")

        if name in self.disabled_names:
            self.disabled_names.remove(name)
        if name not in self.enabled_names:
            self.enabled_names.append(name)

        if name not in self.active_plugins:
            p_config = self.plugin_configs.get(name, {})
            try:
                instance = plugin_cls(config=p_config)
                instance.initialize(context=context)
                self.active_plugins[name] = instance
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error initializing enabled plugin '{name}': {e}")

        self.save_config()

    def disable_plugin(self, name: str, reason: str | None = None) -> None:
        """Disable a plugin by name, call shutdown(), and save configuration."""
        if name in self.enabled_names:
            self.enabled_names.remove(name)
        if name not in self.disabled_names:
            self.disabled_names.append(name)

        if name in self.active_plugins:
            plugin = self.active_plugins.pop(name)
            try:
                plugin.shutdown()
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error shutting down disabled plugin '{name}': {e}")

        if reason:
            if name not in self.execution_errors:
                self.execution_errors[name] = []
            self.execution_errors[name].append(reason)

        self.save_config()

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> dict[str, Any]:
        """
        Safely trigger an event hook across all enabled plugins with strict fault isolation.
        An exception raised inside any plugin will be caught, logged, and auto-disable the faulty plugin without crashing Prometra.
        """
        results: dict[str, Any] = {}

        for name in list(self.active_plugins.keys()):
            plugin = self.active_plugins.get(name)
            if not plugin or not getattr(plugin, "enabled", True):
                continue

            hook_method = getattr(plugin, hook_name, None)
            if hook_method and callable(hook_method):
                try:
                    res = hook_method(*args, **kwargs)
                    results[name] = res
                except Exception as e:  # noqa: BLE001
                    err_msg = f"Fault isolation triggered: Plugin '{name}' raised error in '{hook_name}': {e}"
                    logger.error(err_msg)
                    # Record error and auto-disable faulty plugin to prevent further crashes
                    self.disable_plugin(name, reason=err_msg)

        return results

    def get_status_summary(self) -> list[dict[str, Any]]:
        """Return status breakdown for all registered plugins."""
        summary = []
        for name, plugin_cls in self.registry._plugins.items():
            status = "enabled" if name in self.enabled_names else "disabled"
            summary.append(
                {
                    "name": name,
                    "version": getattr(plugin_cls, "version", "0.1.0"),
                    "author": getattr(plugin_cls, "author", ""),
                    "description": getattr(plugin_cls, "description", ""),
                    "status": status,
                }
            )
        return summary
