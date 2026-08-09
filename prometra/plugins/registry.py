
from prometra.plugins.base import BasePlugin
from prometra.plugins.exceptions import DuplicatePluginError


class PluginRegistry:
    """Registry for managing registered plugin classes."""

    def __init__(self, register_defaults: bool = True):
        self._plugins: dict[str, type[BasePlugin]] = {}
        if register_defaults:
            self.register_builtin_examples()

    def register(self, plugin_cls: type[BasePlugin], overwrite: bool = False) -> None:
        """Register a plugin class."""
        if not issubclass(plugin_cls, BasePlugin):
            raise TypeError(f"Class '{plugin_cls}' must be a subclass of BasePlugin.")

        name = plugin_cls.name
        if not name or name == "BasePlugin":
            name = plugin_cls.__name__

        if name in self._plugins and not overwrite:
            raise DuplicatePluginError(
                f"Plugin with name '{name}' is already registered."
            )

        self._plugins[name] = plugin_cls

    def unregister(self, name: str) -> None:
        """Unregister a plugin by name."""
        if name in self._plugins:
            del self._plugins[name]

    def get(self, name: str) -> type[BasePlugin] | None:
        """Retrieve a registered plugin class by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[type[BasePlugin]]:
        """List all registered plugin classes."""
        return list(self._plugins.values())

    def list_names(self) -> list[str]:
        """List all registered plugin names."""
        return list(self._plugins.keys())

    def register_builtin_examples(self) -> None:
        """Register default built-in example plugins."""
        from prometra.plugins.examples import (
            HelloPlugin,
            SlackNotifier,
            StatisticsPlugin,
        )

        for p_cls in (HelloPlugin, SlackNotifier, StatisticsPlugin):
            self._plugins[p_cls.name] = p_cls
