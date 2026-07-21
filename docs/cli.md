# Prometra CLI Guide

The Typer CLI exposes the following utilities:

## Tracking
- `prometra init`: Scaffold `.prometra` and initialize SQLite.
- `prometra start`: Run the synchronous blocking event loop tracking FS & Git events. Use Ctrl+C to stop.
- `prometra stop`: Remotely stop a running session from another terminal window.

## Analysis
- `prometra analyze`: Read the DB and compute the project's health score.
- `prometra report`: Compile all tracked metrics into `.prometra/reports/` (JSON, CSV, MD, HTML).

## Queries
- `prometra status`: Query the SQLite database for current session length and file changes.
- `prometra history [--json] [--session ID]`: Extract previous session durations.
- `prometra timeline [--markdown] [--json]`: Dump the sequential chronological history of the project.

## Maintenance
- `prometra doctor`: Verify python version, SQLite availability, and Git tracking capability.
- `prometra config`: Print current config variables.
- `prometra version`: Print application and DB schema versions.
- `prometra export`: Run report generation and package everything into `.prometra/export/prometra_export_<proj>.zip`.
