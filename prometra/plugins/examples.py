from typing import Dict, Any, List
from prometra.plugins.base import BasePlugin

class HelloPlugin(BasePlugin):
    """Example plugin that logs session lifecycle events."""

    name = "HelloPlugin"
    version = "1.0.0"
    author = "Prometra Team"
    description = "Logs session start and end events."

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logs: List[str] = []

    def initialize(self, context: Dict[str, Any] = None) -> None:
        self.logs.append("HelloPlugin initialized.")

    def on_session_started(self, session_data: Dict[str, Any]) -> None:
        msg = f"[HelloPlugin] Session started: {session_data.get('session_id')}"
        self.logs.append(msg)

    def on_session_ended(self, session_data: Dict[str, Any]) -> None:
        msg = f"[HelloPlugin] Session ended: {session_data.get('session_id')}"
        self.logs.append(msg)

class SlackNotifier(BasePlugin):
    """Example mock plugin for sending Slack notifications."""

    name = "SlackNotifier"
    version = "1.0.0"
    author = "Prometra Team"
    description = "Mock notification plugin for Slack integration."

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.notifications: List[str] = []

    def on_session_started(self, session_data: Dict[str, Any]) -> None:
        url = self.config.get("webhook_url", "mock://slack.webhook")
        note = f"[Slack] Posted to {url}: Session {session_data.get('session_id')} started."
        self.notifications.append(note)

    def on_file_changed(self, event_data: Dict[str, Any]) -> None:
        path = event_data.get("path") or event_data.get("normalized_relative_path")
        note = f"[Slack] Notification: File changed - {path}"
        self.notifications.append(note)

class StatisticsPlugin(BasePlugin):
    """Example plugin that counts file changes in memory."""

    name = "StatisticsPlugin"
    version = "1.0.0"
    author = "Prometra Team"
    description = "In-memory file change counter plugin."

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.file_change_count: int = 0
        self.changed_files: List[str] = []

    def on_file_changed(self, event_data: Dict[str, Any]) -> None:
        self.file_change_count += 1
        path = event_data.get("path") or event_data.get("normalized_relative_path") or "unknown"
        if path not in self.changed_files:
            self.changed_files.append(path)
