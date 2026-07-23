import os
import sys
import importlib.util
import inspect
from typing import List, Type, Optional, Dict, Any

from prometra.plugins.base import BasePlugin
from prometra.plugins.registry import PluginRegistry
from prometra.plugins.exceptions import PluginLoadError

class PluginLoader:
    """Discovers and dynamically loads Prometra plugins from specified directories."""

    def __init__(self, registry: Optional[PluginRegistry] = None, search_paths: Optional[List[str]] = None):
        self.registry = registry or PluginRegistry()
        self.search_paths: List[str] = search_paths or self._default_search_paths()
        self.load_errors: Dict[str, str] = {}

    @staticmethod
    def _default_search_paths() -> List[str]:
        """Return default plugin discovery search paths."""
        user_path = os.path.expanduser("~/.prometra/plugins")
        local_path = os.path.abspath(os.path.join(".prometra", "plugins"))
        paths = []
        if os.path.exists(user_path):
            paths.append(user_path)
        if os.path.exists(local_path):
            paths.append(local_path)
        return paths

    def discover_and_load(self) -> List[Type[BasePlugin]]:
        """Scan search paths, dynamically load valid BasePlugin classes, and register them."""
        loaded_classes: List[Type[BasePlugin]] = []

        for directory in self.search_paths:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                continue

            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        plugin_clss = self.load_plugin_from_file(file_path)
                        for p_cls in plugin_clss:
                            try:
                                self.registry.register(p_cls, overwrite=False)
                                loaded_classes.append(p_cls)
                            except Exception as e:
                                self.load_errors[file_path] = str(e)

        return loaded_classes

    def load_plugin_from_file(self, file_path: str) -> List[Type[BasePlugin]]:
        """Dynamically load a Python file and return any BasePlugin subclasses defined within it."""
        discovered: List[Type[BasePlugin]] = []
        module_name = f"prometra_plugin_{os.path.splitext(os.path.basename(file_path))[0]}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                self.load_errors[file_path] = "Failed to create module spec."
                return discovered

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    # Ensure plugin is defined in the loaded module (not imported)
                    if obj.__module__ == module_name or getattr(obj, "name", None):
                        discovered.append(obj)

        except Exception as e:
            self.load_errors[file_path] = f"Load error: {str(e)}"

        return discovered
