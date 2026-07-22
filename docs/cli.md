# Prometra CLI Guide

The Typer CLI exposes the following utilities:

## Tracking
- `prometra init`: Scaffold `.prometra` and initialize SQLite.
- `prometra start`: Run the synchronous blocking event loop tracking FS & Git events. Use Ctrl+C to stop.
- `prometra stop`: Remotely stop a running session from another terminal window.

## Analysis
- `prometra analyze`: Read the DB and compute the project's health score.
- `prometra report`: Compile all tracked metrics into `.prometra/reports/` (JSON, CSV, MD, HTML).
- `prometra dashboard [OPTIONS]`: Render interactive development analytics dashboard with time windows (`--today`, `--week`, `--month`), session filtering (`--session`), top edited files, top AI models, token costs, and exports (`--export dashboard.md|json`).

## Queries
- `prometra status`: Query the SQLite database for current session length and file changes.
- `prometra history [--json] [--session ID]`: Extract previous session durations.
- `prometra timeline [OPTIONS]`: Interactive timeline explorer with rich tables, colorization, search, filtering (`--session`, `--type`, `--connector`, `--search`, `--today`, `--limit`, `--reverse`), session grouping (`--group session`), summary statistics (`--summary`), and file export (`--export timeline.md|csv|json`).
- `prometra replay [OPTIONS]`: Reconstruct and play back a coding session with animated speeds (`1x`, `2x`, `5x`, `10x`, `instant`), step mode (`--step`), and multi-format exports (`--export replay.md|json`).
- `prometra search QUERY [OPTIONS]`: Instantly search recorded events stored in SQLite with category filters (`--type`), session filtering (`--session`), date range filtering (`--today`, `--week`, `--since`, `--until`), result limit (`--limit`), text highlighting, and JSON/Markdown/export options (`--json`, `--markdown`, `--export search.md|json`).

## Maintenance
- `prometra doctor`: Verify python version, SQLite availability, and Git tracking capability.
- `prometra config`: Print current config variables.
- `prometra version`: Print application and DB schema versions.
- `prometra export`: Run report generation and package everything into `.prometra/export/prometra_export_<proj>.zip`.

## Connectors (V2 SDK)
- `prometra connectors list`: Show all discovered external connectors via Python `entry_points`.
- `prometra connectors info <name>`: View specific connector metadata and capabilities.
- `prometra connectors enable <name>`: Turn on an installed AI connector.
- `prometra connectors disable <name>`: Turn off an installed AI connector.
- `prometra connectors health`: Ping all enabled connectors and report their HTTP/Socket health.
- `prometra connectors validate`: Run configuration and schema checks against installed plugins.
