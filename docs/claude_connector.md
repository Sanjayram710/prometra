# Claude Code Connector

The Claude Code Connector is Prometra's flagship implementation of the V2 Connector SDK. It discovers local installations of Anthropic's Claude Code CLI, monitors session lifecycle, and translates AI interactions into provider-agnostic events for the Timeline Engine.

## Features
- **Auto-Discovery**: Locates `claude` (or `claude.cmd` on Windows) via system PATH.
- **Event Bus Streaming**: Emits typed Claude events (`ClaudePromptSubmitted`, `ClaudeResponseReceived`, `ClaudeToolInvocationStarted`, `ClaudeTokenUsage`, `ClaudeCostRecorded`, `ClaudeErrorOccurred`).
- **Generic Event Translation**: Integrates with `ai_translator_registry` to convert Claude-specific events into normalized `AiEvent` instances.
- **Decoupled Architecture**: Publishes events via `EventBus` without writing directly to SQLite. The `TimelineEngine` handles database persistence.

## Lifecycle & Flow
1. `initialize()`: Connects to local storage configuration.
2. `connect()`: Scans the system for the Claude Code binary, updates health state, and emits `ClaudeConnected`.
3. `emit_event()`: Translates connector events into generic `AiEvent` objects and publishes them onto the `EventBus`.
4. `disconnect()`: Emits `ClaudeDisconnected` and releases resources gracefully.
