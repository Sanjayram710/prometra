from typing import Any


class BasePlugin:
    """Abstract base class for all Prometra plugins."""

    name: str = "BasePlugin"
    version: str = "0.1.0"
    author: str = ""
    description: str = ""
    enabled: bool = True

    def __init__(self, config: dict[str, Any] | None = None):
        self.config: dict[str, Any] = config or {}

    def initialize(self, context: dict[str, Any] | None = None) -> None:
        """Lifecycle hook called when the plugin is loaded and initialized."""

    def shutdown(self) -> None:
        """Lifecycle hook called when the plugin is being shut down."""

    # Optional Event Hooks
    def on_session_started(self, session_data: dict[str, Any]) -> None:
        """Event hook triggered when a new tracking session starts."""

    def on_session_ended(self, session_data: dict[str, Any]) -> None:
        """Event hook triggered when a tracking session ends."""

    def on_file_changed(self, event_data: dict[str, Any]) -> None:
        """Event hook triggered when a file creation, modification, or deletion is recorded."""

    def on_git_commit(self, event_data: dict[str, Any]) -> None:
        """Event hook triggered when a Git commit is recorded."""

    def on_search(self, query_data: dict[str, Any]) -> None:
        """Event hook triggered when an intelligent search is executed."""

    def on_diff(self, diff_data: dict[str, Any]) -> None:
        """Event hook triggered when a file diff is generated."""

    def on_compare(self, compare_data: dict[str, Any]) -> None:
        """Event hook triggered when a session comparison is executed."""

    def metadata(self) -> dict[str, Any]:
        """Return metadata describing the plugin."""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "enabled": self.enabled,
        }
