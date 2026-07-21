# Connector SDK Developer Guide

Prometra Version 2 supports an extensible plugin architecture to integrate AI models and cloud sync services without modifying core tracking functionality.

## Core Concepts
- **`BaseConnector`**: The abstract base class all plugins must implement (`prometra/connectors/base.py`).
- **`ConnectorRegistry`**: Automatically discovers installed plugins via `entry_points`.
- **`EventBus`**: Exposes typed Pydantic events (`SessionStarted`, `GitCommit`) that your connector can subscribe to.

## Building a Plugin

1. Create a Python package (e.g., `prometra-claude`).
2. Implement `BaseConnector`.
3. In your `setup.py` or `pyproject.toml`, expose the entry point:
   ```toml
   [project.entry-points."prometra.connectors"]
   claude = "prometra_claude.connector:ClaudeConnector"
   ```
4. When a user runs `pip install prometra-claude`, Prometra automatically loads it into the `ConnectorRegistry`.
