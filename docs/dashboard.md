# Prometra Analytics Dashboard

The **Analytics Dashboard** (`prometra dashboard`) provides real-time development intelligence aggregated across sessions, filesystem edits, Git commits, AI prompts, token consumption, and estimated API costs.

## Features

- **Session Intelligence**: Total sessions, cumulative development duration, longest session, average session length.
- **Filesystem & Git Activity**: Files created, modified, deleted, and git commits per day.
- **AI Metrics**: Total prompts, responses, tool calls, diagnostic errors, retries, input/output token usage, and cost estimation.
- **Top Rankings**: Ranked tables for most-edited codebase files and top AI models used.
- **Peak Activity Hours**: Identification of peak development productivity hours.
- **Multi-Format Exports**: Support for Markdown and JSON report exports.

## Usage & Command Options

### 1. View Default All-Time Dashboard
```bash
prometra dashboard
```

### 2. Time Window Filtering
Filter analytics by specific time windows:
```bash
prometra dashboard --today    # Today's activity
prometra dashboard --week     # Past 7 days
prometra dashboard --month    # Past 30 days
```

### 3. Session Filtering
Inspect analytics for a specific session:
```bash
prometra dashboard --session sess-1234
```

### 4. Output & Export Options
Output raw JSON, Markdown, or export directly to a file:
```bash
prometra dashboard --json
prometra dashboard --markdown
prometra dashboard --export dashboard.md
prometra dashboard --export dashboard.json
```

## SQL Aggregation Architecture

The dashboard engine performs optimized SQLite aggregation queries (`COUNT`, `SUM`, `AVG`, `GROUP BY`) across tables:
- `sessions`: Session counts and durations
- `filesystem_events`: File modification counts and top edited file rankings
- `git_events`: Repository commit counts
- `ai_events`: Prompt counts, token counts, model rankings, cost calculations
- `timeline_events`: Event sequencing and peak active hour patterns
