# Prometra Interactive Timeline

The **Interactive Timeline** in Prometra transforms sequential project history into a feature-rich CLI explorer. It allows developers, team leads, and AI auditors to search, filter, group, summarize, and export developer timeline events in real-time.

## Features & Usage

### 1. Filtering by Session
Restrict timeline output to a single session ID:
```bash
prometra timeline --session sess-1234
```

### 2. Filtering by Category / Event Type
Show events matching specific categories (`filesystem`, `git`, `ai`, `connector`, `session`):
```bash
prometra timeline --type git
prometra timeline --type ai
prometra timeline --type filesystem
```

### 3. Filtering by AI Connector
Show timeline events produced by a specific AI tool or connector:
```bash
prometra timeline --connector claude
```

### 4. Searching Descriptions
Perform fast SQL search across event descriptions, summaries, and tools:
```bash
prometra timeline --search "authentication"
```

### 5. Today's Events
Restrict timeline view to events created today (UTC date boundary):
```bash
prometra timeline --today
```

### 6. Pagination & Limits
Limit returned events for responsive exploration on massive repositories (100,000+ events):
```bash
prometra timeline --limit 50
```

### 7. Reverse Chronological Order
View newest events first:
```bash
prometra timeline --reverse
```

### 8. Session Grouping
Group events by session with detailed header cards including session duration, file count, git commit count, and AI event count:
```bash
prometra timeline --group session
```

### 9. Timeline Summary
Display high-level timeline metric dashboards:
```bash
prometra timeline --summary
```

### 10. Multi-Format Export
Export timeline queries to Markdown, CSV, or JSON format:
```bash
prometra timeline --export timeline.md
prometra timeline --export timeline.csv
prometra timeline --export timeline.json
```

## Category Colorization Scheme

| Category | Terminal Color | Description |
| --- | --- | --- |
| **Filesystem** | `Green` | File creation, modification, deletion |
| **Git** | `Blue` | Branch, commit, merge events |
| **AI** | `Magenta` | Prompts, completions, model selection, context events |
| **Connector** | `Yellow` | Connector status & plugin lifecycle events |
| **Session** | `Cyan` | Session start and stop events |
| **Errors** | `Red` | System or connector diagnostic errors |
