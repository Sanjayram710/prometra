# File Diff Viewer Documentation

The File Diff Viewer (`prometra diff`) allows users to inspect line-by-line changes between tracked file versions entirely locally using Python standard library `difflib`.

## Overview

Prometra records file modifications and AI tool operations into SQLite event history. The File Diff Viewer queries this event history to reconstruct file states at specific event sequence checkpoints and computes unified diffs.

## CLI Usage

```bash
prometra diff FILE_PATH [OPTIONS]
```

### Options

- `FILE_PATH` *(Required)*: Path or filename of the file to inspect.
- `--session TEXT`: Filter event history to a specific session ID.
- `--from-event INTEGER`: Specify the starting event ID (sequence checkpoint).
- `--to-event INTEGER`: Specify the ending event ID (sequence checkpoint).
- `--latest`: Compare the latest two recorded versions of the file.
- `--context INTEGER` *(Default: 3)*: Set number of surrounding context lines in diff output.
- `--json`: Format output as a JSON object.
- `--markdown`: Format output as a Markdown document.

## Examples

### 1. Basic Terminal Diff

Compare the latest two versions of `hello.py`:

```bash
prometra diff hello.py
```

**Terminal Output:**

```
------------------------------------------------
File
hello.py

Compared
Event 2
↓
Event 3

@@ -1,1 +1,2 @@
- print("Hello")
+ print("Hello World")
------------------------------------------------
```

### 2. Diffing Specific Events

Compare Event 12 and Event 20:

```bash
prometra diff hello.py --from-event 12 --to-event 20
```

### 3. Session-Filtered Diff

Inspect changes for `hello.py` within a specific session:

```bash
prometra diff hello.py --session sess-9f8a3d12
```

### 4. JSON Export

Output diff data in structured JSON format:

```bash
prometra diff hello.py --json
```

**JSON Output Example:**

```json
{
  "file": "hello.py",
  "event_from": 2,
  "event_to": 3,
  "session_id": "sess-9f8a3d12",
  "timestamp_from": "2026-07-23T12:00:00+00:00",
  "timestamp_to": "2026-07-23T12:30:00+00:00",
  "added_lines": 4,
  "removed_lines": 2,
  "modified_lines": 1,
  "diff": "--- Event 2\n+++ Event 3\n@@ -1,2 +1,4 @@\n- print(\"Hello\")\n+ print(\"Hello World\")\n"
}
```

### 5. Markdown Export

Output diff report as Markdown:

```bash
prometra diff hello.py --markdown
```

**Markdown Output Example:**

```markdown
# File Diff

- **File:** `hello.py`
- **Compared:** Event 2 → Event 3
- **Session ID:** `sess-9f8a3d12`
- **Timestamp From:** `2026-07-23T12:00:00+00:00`
- **Timestamp To:** `2026-07-23T12:30:00+00:00`
- **Stats:** +4 added, -2 removed, ~1 modified

```diff
--- Event 2
+++ Event 3
@@ -1,2 +1,4 @@
- print("Hello")
+ print("Hello World")
```
```

## Performance & Privacy

- **Performance**: Executed in <50ms for files up to 1,000 lines.
- **Privacy & Security**: Runs 100% locally. No external APIs, cloud connections, or third-party diff dependencies.
