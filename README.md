# Prometra

**The Intelligence Layer for AI-Assisted Software Development**

Prometra is a local-first development intelligence tracker that records session metrics, filesystem operations, and Git history natively into SQLite without requiring cloud sync.

## Version 1 Finalization

The V1 milestone is complete, focusing strictly on local-first data integrity, chronological timeline generation, and comprehensive offline reporting.

## Installation

```bash
pip install -e .[dev]
```

## Available Commands

* `prometra init`: Initialize a local `.prometra` repository.
* `prometra start`: Begin tracking the filesystem and Git history in a background loop.
* `prometra stop`: Gracefully halt the active session.
* `prometra status`: View real-time active tracking state.
* `prometra history`: Review past sessions.
* `prometra timeline`: View a chronological log of all captured events.
* `prometra doctor`: Run a diagnostic system check.
* `prometra config`: View active settings.
* `prometra version`: Print current application schema and version.
* `prometra analyze`: Compute a health score and risk analysis.
* `prometra report`: Generate Markdown, HTML, CSV, and JSON outputs.
* `prometra export`: Package database and reports into a ZIP archive.

For details, refer to `docs/cli.md` and `docs/architecture.md`.
