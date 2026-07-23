from typing import Dict, Any, Optional

class BasePlugin:
    """Abstract base class for all Prometra plugins."""

    name: str = "BasePlugin"
    version: str = "0.1.0"
    author: str = ""
    description: str = ""
    enabled: bool = True

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config: Dict[str, Any] = config or {}

    def initialize(self, context: Optional[Dict[str, Any]] = None) -> None:
        """Lifecycle hook called when the plugin is loaded and initialized."""
        pass

    def shutdown(self) -> None:
        """Lifecycle hook called when the plugin is being shut down."""
        pass

    # Optional Event Hooks
    def on_session_started(self, session_data: Dict[str, Any]) -> None:
        """Event hook triggered when a new tracking session starts."""
        pass

    def on_session_ended(self, session_data: Dict[str, Any]) -> None:
        """Event hook triggered when a tracking session ends."""
        pass

    def on_file_changed(self, event_data: Dict[str, Any]) -> None:
        """Event hook triggered when a file creation, modification, or deletion is recorded."""
        pass

    def on_git_commit(self, event_data: Dict[str, Any]) -> None:
        """Event hook triggered when a Git commit is recorded."""
        pass

    def on_search(self, query_data: Dict[str, Any]) -> None:
        """Event hook triggered when an intelligent search is executed."""
        pass

    def on_diff(self, diff_data: Dict[str, Any]) -> None:
        """Event hook triggered when a file diff is generated."""
        pass

    def on_compare(self, compare_data: Dict[str, Any]) -> None:
        """Event hook triggered when a session comparison is executed."""
        pass

    def metadata(self) -> Dict[str, Any]:
        """Return metadata describing the plugin."""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "enabled": self.enabled
        }
