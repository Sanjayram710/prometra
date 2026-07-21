# Claude Code Connector

The Claude Code Connector is Prometra's flagship implementation of the V2 Connector SDK. It discovers local installations of Anthropic's Claude Code CLI, monitors session lifecycle, and aggregates context deterministically.

## Features
- **Auto-Discovery**: Locates `claude` (or `claude.cmd` on Windows) via system paths.
- **Session Tracking**: Exposes the architecture for polling active sessions and intercepts lifecycle events (`ClaudeSessionStarted`, `ClaudeSessionStopped`).
- **Data Persistence**: Inherits Prometra's `SQLiteStorage` context to save events directly into the `TimelineEventModel`.
- **SDK Extensibility**: Implements `BaseConnector`, yielding its own custom typed metadata.

## Lifecycle
1. `initialize()`: Connects to the local `.prometra/prometra.db`.
2. `connect()`: Scans the system for the Claude Code binary using `shutil.which`. If found, checks the version via subprocess and goes into `connected` state.
3. `capture()`: Builds a rigorous context tree using `ContextBuilder` and bundles it with the dynamically generated connector metadata.
