# Session Comparison Documentation

The **Session Comparison Engine** (`prometra compare`) allows developers to compare two recorded development sessions side-by-side to analyze productivity, file edits, Git commits, AI events, duration differences, and timeline distributions.

## Overview

Session comparison queries the local SQLite database to aggregate session metadata, filesystem edits, Git activity, and AI events for two target sessions, computing exact differences and productivity rates.

## CLI Usage

```bash
prometra compare [SESSION_A] [SESSION_B] [OPTIONS]
```

### Options

- `SESSION_A`: Optional ID of the first session to compare.
- `SESSION_B`: Optional ID of the second session to compare.
- `--latest`: Compare the two most recent recorded sessions automatically.
- `--json`: Output comparison metrics as JSON.
- `--markdown`: Output comparison report as Markdown.
- `--export PATH`: Save comparison output to specified file path.
- `--help`: Display CLI help documentation.

## Examples

### 1. Basic Terminal Comparison

Compare two specific sessions:

```bash
prometra compare sess-a1b2c3d4 sess-e5f6g7h8
```

**Terminal Output Example:**

```
--------------------------------------------------

Session Comparison

Session A (sess-a1b2c3d4)

Duration
15 min

Files Modified
12

Git Commits
3

AI Events
7

------------ VS ------------

Session B (sess-e5f6g7h8)

Duration
24 min

Files Modified
21

Git Commits
6

AI Events
4

Difference

+9 min
+9 files
+3 commits
-3 AI events

--------------------------------------------------
```

### 2. Compare Latest Two Sessions

```bash
prometra compare --latest
```

### 3. JSON Output

```bash
prometra compare sess-a1b2c3d4 sess-e5f6g7h8 --json
```

**JSON Output Example:**

```json
{
  "session_a": "sess-a1b2c3d4",
  "session_b": "sess-e5f6g7h8",
  "duration_difference": "+9 min",
  "files_created_difference": 0,
  "files_modified_difference": 9,
  "files_deleted_difference": 0,
  "git_commit_difference": 3,
  "ai_event_difference": -3,
  "timeline_difference": {
    "total_events_a": 22,
    "total_events_b": 31,
    "total_events_difference": 9,
    "event_type_distribution_a": {
      "filesystem": 12,
      "git": 3,
      "ai": 7
    },
    "event_type_distribution_b": {
      "filesystem": 21,
      "git": 6,
      "ai": 4
    }
  }
}
```

### 4. Markdown Output & Export

```bash
prometra compare --latest --markdown --export docs/compare_report.md
```

## Performance & Security

- **Performance**: Executed in <75 ms for session metrics lookup.
- **Privacy & Security**: Operates 100% locally on local SQLite database history.
