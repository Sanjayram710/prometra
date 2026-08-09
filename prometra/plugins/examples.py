from typing import Any

from prometra.plugins.base import BasePlugin


class HelloPlugin(BasePlugin):
    """Example plugin that logs session lifecycle events."""

    name = "HelloPlugin"
    version = "1.0.0"
    author = "Prometra Team"
    description = "Logs session start and end events."

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.logs: list[str] = []

    def initialize(self, context: dict[str, Any] | None = None) -> None:
        self.logs.append("HelloPlugin initialized.")

    def on_session_started(self, session_data: dict[str, Any]) -> None:
        msg = f"[HelloPlugin] Session started: {session_data.get('session_id')}"
        self.logs.append(msg)

    def on_session_ended(self, session_data: dict[str, Any]) -> None:
        msg = f"[HelloPlugin] Session ended: {session_data.get('session_id')}"
        self.logs.append(msg)


class SlackNotifier(BasePlugin):
    """Example mock plugin for sending Slack notifications."""

    name = "SlackNotifier"
    version = "1.0.0"
    author = "Prometra Team"
    description = "Mock notification plugin for Slack integration."

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.notifications: list[str] = []

    def on_session_started(self, session_data: dict[str, Any]) -> None:
        url = self.config.get("webhook_url", "mock://slack.webhook")
        note = f"[Slack] Posted to {url}: Session {session_data.get('session_id')} started."
        self.notifications.append(note)

    def on_file_changed(self, event_data: dict[str, Any]) -> None:
        path = event_data.get("path") or event_data.get("normalized_relative_path")
        note = f"[Slack] Notification: File changed - {path}"
        self.notifications.append(note)


class StatisticsPlugin(BasePlugin):
    """Example plugin that counts file changes in memory."""

    name = "StatisticsPlugin"
    version = "1.0.0"
    author = "Prometra Team"
    description = "In-memory file change counter plugin."

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.file_change_count: int = 0
        self.changed_files: list[str] = []

    def on_file_changed(self, event_data: dict[str, Any]) -> None:
        self.file_change_count += 1
        path = event_data.get("path") or event_data.get("normalized_relative_path")
        if path:
            self.changed_files.append(str(path))
