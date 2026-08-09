import contextlib
from importlib.metadata import entry_points

from prometra.connectors.base import BaseConnector
from prometra.connectors.exceptions import ConnectorRegistrationError


class ConnectorRegistry:
    """Registry to discover and hold connector classes."""

    def __init__(self):
        self._connectors: dict[str, type[BaseConnector]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register core built-in connectors."""
        with contextlib.suppress(Exception):
            from prometra.connectors.claude import ClaudeConnector
            self._connectors["claude"] = ClaudeConnector

        with contextlib.suppress(Exception):
            from prometra.connectors.gemini import GeminiConnector
            self._connectors["gemini"] = GeminiConnector

        with contextlib.suppress(Exception):
            from prometra.connectors.gpt import GPTConnector
            self._connectors["gpt"] = GPTConnector

        with contextlib.suppress(Exception):
            from prometra.connectors.mcp import MCPConnector
            self._connectors["mcp"] = MCPConnector

        with contextlib.suppress(Exception):
            from prometra.connectors.antigravity import AntigravityConnector
            self._connectors["antigravity"] = AntigravityConnector

        with contextlib.suppress(Exception):
            from prometra.connectors.codex import CodexConnector
            self._connectors["codex"] = CodexConnector

    def register(self, name: str, connector_class: type[BaseConnector]) -> None:
        """Manually register a connector class."""
        if name in self._connectors:
            raise ConnectorRegistrationError(
                f"Connector '{name}' is already registered."
            )

        self.validate(connector_class)
        self._connectors[name] = connector_class

    def unregister(self, name: str) -> None:
        """Unregister a connector class."""
        if name in self._connectors:
            del self._connectors[name]

    def get(self, name: str) -> type[BaseConnector]:
        """Get a registered connector class by name."""
        if name not in self._connectors:
            raise KeyError(f"Connector '{name}' not found.")
        return self._connectors[name]

    def list(self) -> list[str]:
        """List all registered connector names."""
        return list(self._connectors.keys())

    def validate(self, connector_class: type[BaseConnector]) -> None:
        """Validate that the class properly implements BaseConnector."""
        if not issubclass(connector_class, BaseConnector):
            raise ConnectorRegistrationError(
                f"{connector_class.__name__} must inherit from BaseConnector."
            )

    def discover_plugins(self) -> None:
        """Discover external plugins via importlib.metadata entry_points."""
        with contextlib.suppress(Exception):
            eps = entry_points(group="prometra.connectors")
            for ep in eps:
                with contextlib.suppress(Exception):
                    plugin_class = ep.load()
                    name = ep.name
                    if name not in self._connectors:
                        self.register(name, plugin_class)
