# Prometra Interactive Timeline

The **Interactive Timeline** in Prometra transforms sequential project history into a feature-rich CLI explorer. It connects filesystem changes, Git state, and generic AI events into a unified chronological stream.

## AI Event Pipeline

AI events flow seamlessly from connectors to the timeline:
```
Connector -> Generic AI Event -> Event Bus -> Timeline Engine -> SQLite -> Timeline CLI
```

All 18 standard AI event types (`PromptSubmitted`, `PromptUpdated`, `ResponseStarted`, `ResponseReceived`, `ResponseCompleted`, `ToolInvocationStarted`, `ToolInvocationCompleted`, `ToolInvocationFailed`, `TokenUsage`, `CostRecorded`, `ModelChanged`, `ContextInjected`, `ErrorOccurred`, `RetryAttempt`, `ConnectorConnected`, `ConnectorDisconnected`, `SessionStarted`, `SessionEnded`) are persisted in SQLite and displayed alongside developer activity.

## Features & Usage

### 1. Filtering AI Events
Show all AI events or filter by specific connector:
```bash
prometra timeline --type ai
prometra timeline --connector claude
```

### 2. Searching Prompts & Tools
Perform fast SQL search across prompts, tool calls, and event descriptions:
```bash
prometra timeline --search prompt
prometra timeline --search tool
```

### 3. Session Grouping
Group events by session with detailed header cards including session duration, file count, git commit count, and AI event count:
```bash
prometra timeline --group session
```

### 4. Timeline Summary Statistics
Display aggregated timeline dashboards including AI metrics:
```bash
prometra timeline --summary
```

**Example Summary Output:**
- Sessions
- Files Modified
- Git Commits
- AI Prompts
- AI Responses
- Tool Calls
- Token Usage (Total, Input, Output)
- Estimated Cost ($)
- Connectors Used
- Total Events

### 5. Multi-Format Export
Export timeline queries to Markdown, CSV, or JSON format:
```bash
prometra timeline --export timeline.md
prometra timeline --export timeline.csv
prometra timeline --export timeline.json
```

## Colorization Scheme

| Category / Event Type | Terminal Color | Description |
| --- | --- | --- |
| **AI Events** | `Magenta` | General AI model & session events |
| **Prompts** | `Bright Cyan` | Prompt submissions & prompt updates |
| **Responses** | `Green` | AI responses & completions |
| **Tool Calls** | `Yellow` | Tool invocation start, complete, & fail |
| **Filesystem** | `Green` | File creation, modification, deletion |
| **Git** | `Blue` | Branch, commit, merge events |
| **Session** | `Cyan` | Session start and stop events |
| **Errors** | `Red` | Diagnostic & execution errors |
