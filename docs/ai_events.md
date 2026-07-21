# Provider-Agnostic AI Event Model

Prometra centralizes AI analysis by enforcing a strictly agnostic event structure. Rather than storing events like `ClaudeSessionStarted` or `GeminiToolCall`, the core system maps everything into a single, unified ontology.

## The Models
Located in `prometra/ai/events.py`, standard models include:
- `PromptSubmitted`
- `ResponseReceived`
- `ToolInvocation`
- `ModelSelected`
- `TokenUsage`
- `LatencyMeasured`

## The Translation Layer
Connectors define their own specialized events to capture nuances of their respective services. Before these events hit the `TimelineEngine` or SQLite storage, they pass through the `EventTranslatorRegistry` (`prometra/ai/translators.py`), guaranteeing that only standard `AiEvent` objects reach the database.

## Metrics
The `AiMetricsAggregator` computes total token costs, latency averages, and error rates using *only* the standardized events. This ensures that when new connectors are introduced, the analytical reports automatically support them with zero codebase changes.
