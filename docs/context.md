# Context Assembly Engine

The Context Engine (`prometra/context`) bridges Prometra's raw V1 data tracking layer with V2's external connector ecosystem.

## Goal
Rather than requiring connectors to write SQL queries against `prometra.db`, the Context Engine aggregates all recent file changes, git states, and health scores into a strict Pydantic model (`prometra.context.models.Context`).

## Implementation
- **Read-Only**: The `ContextBuilder` never mutates data.
- **Aggregated Model**: Outputs a heavily typed tree (`ProjectState`, `TimelineSummary`) perfect for injecting into system prompts.
- **Decoupled**: Independent of the prompt generation layer, allowing varying AI models to parse the unified format.
