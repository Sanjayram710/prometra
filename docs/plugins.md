# Plugin System & Extension Framework Documentation

Prometra features a local-first **Plugin Architecture** allowing developers to extend Prometra's tracking, reporting, notification, and event capabilities without modifying the core codebase.

---

## Architecture & Concepts

Prometra plugins are Python modules that inherit from `BasePlugin`. Plugins can subscribe to lifecycle hooks (`initialize()`, `shutdown()`) and event hooks (`on_session_started()`, `on_file_changed()`, `on_git_commit()`, `on_search()`, `on_diff()`, `on_compare()`).

### Fault Isolation Guarantee

Prometra enforces **strict fault isolation** for all plugins:

- Uncaught exceptions raised by a plugin during hook execution are safely caught and logged.
- Faulty plugins are automatically disabled in `~/.prometra/plugins.json` to prevent repeated errors.
- **A broken plugin will NEVER crash Prometra core commands.**

---

## Creating a Custom Plugin

Create a Python file (e.g. `my_notifier.py`) inheriting from `prometra.plugins.BasePlugin`:

```python
from typing import Dict, Any
from prometra.plugins import BasePlugin

class AuditNotifierPlugin(BasePlugin):
    name = "AuditNotifierPlugin"
    version = "1.0.0"
    author = "Development Team"
    description = "Logs file modifications for compliance auditing."

    def initialize(self, context: Dict[str, Any] = None) -> None:
        print(f"[{self.name}] Initialized.")

    def on_session_started(self, session_data: Dict[str, Any]) -> None:
        session_id = session_data.get("session_id")
        print(f"[{self.name}] Session started: {session_id}")

    def on_file_changed(self, event_data: Dict[str, Any]) -> None:
        file_path = event_data.get("path") or event_data.get("normalized_relative_path")
        operation = event_data.get("operation", "modified")
        print(f"[{self.name}] Audit Log: File {operation} - {file_path}")

    def shutdown(self) -> None:
        print(f"[{self.name}] Shutting down.")
```

---

## Installing Plugins

Prometra automatically discovers Python plugins placed in either of the following directories:

1. **User Home Plugins Directory**: `~/.prometra/plugins/`
2. **Project Local Plugins Directory**: `.prometra/plugins/`

Simply place your `.py` plugin file into `~/.prometra/plugins/` or `.prometra/plugins/`. Prometra will discover and register the plugin automatically on the next CLI run or reload command.

---

## Plugin Configuration (`plugins.json`)

Plugin enabled status and per-plugin configurations are stored in `~/.prometra/plugins.json`:

```json
{
  "enabled": [
    "HelloPlugin",
    "StatisticsPlugin",
    "AuditNotifierPlugin"
  ],
  "disabled": [
    "SlackNotifier"
  ],
  "config": {
    "SlackNotifier": {
      "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    }
  }
}
```

---

## Built-In Example Plugins

Prometra includes built-in example plugins:

1. **`HelloPlugin`**: Logs session start and session end lifecycle events.
2. **`SlackNotifier`**: Mock notification plugin demonstrating external webhook integration patterns.
3. **`StatisticsPlugin`**: Tracks in-memory file change counts.

---

## CLI Management (`prometra plugins`)

### 1. List Installed Plugins

Display installed plugins, version, enabled/disabled status, author, and description:

```bash
prometra plugins
```

**Terminal Output:**

```
┌──────────────────┬─────────┬──────────┬───────────────┬───────────────────────────────────────────┐
│ Name             │ Version │ Status   │ Author        │ Description                               │
├──────────────────┼─────────┼──────────┼───────────────┼───────────────────────────────────────────┤
│ HelloPlugin      │ 1.0.0   │ enabled  │ Prometra Team │ Logs session start and end events.        │
│ SlackNotifier    │ 1.0.0   │ disabled │ Prometra Team │ Mock notification plugin for Slack.       │
│ StatisticsPlugin │ 1.0.0   │ enabled  │ Prometra Team │ In-memory file change counter plugin.     │
└──────────────────┴─────────┴──────────┴───────────────┴───────────────────────────────────────────┘
```

### 2. Enable a Plugin

```bash
prometra plugins enable HelloPlugin
```

### 3. Disable a Plugin

```bash
prometra plugins disable SlackNotifier
```

### 4. Reload Plugin Discovery

```bash
prometra plugins reload
```

---

## Event Hooks Reference

| Hook Name | Arguments | Description |
| :--- | :--- | :--- |
| `initialize(context)` | `context: Dict[str, Any]` | Triggered when plugin instance is created and loaded. |
| `shutdown()` | None | Triggered when plugin is unloaded or disabled. |
| `on_session_started(data)` | `session_data: Dict[str, Any]` | Triggered when a new tracking session starts. |
| `on_session_ended(data)` | `session_data: Dict[str, Any]` | Triggered when a tracking session stops. |
| `on_file_changed(data)` | `event_data: Dict[str, Any]` | Triggered when a file creation, edit, or deletion occurs. |
| `on_git_commit(data)` | `event_data: Dict[str, Any]` | Triggered when a Git commit is recorded. |
| `on_search(data)` | `query_data: Dict[str, Any]` | Triggered when a search query is executed. |
| `on_diff(data)` | `diff_data: Dict[str, Any]` | Triggered when a file diff is generated. |
| `on_compare(data)` | `compare_data: Dict[str, Any]` | Triggered when two sessions are compared. |
