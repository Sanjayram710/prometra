# Prometra Architecture

Prometra Version 1 is strictly a local-first intelligence application.

## Core Components

1. **Storage Layer (`prometra/storage`)**: Uses SQLAlchemy mapped to a local SQLite database (`.prometra/prometra.db`). Maintains strict timezone-aware UTC schemas using a custom `AwareDateTime` decorator.
2. **Trackers (`prometra/tracker`)**:
   - `FilesystemTracker`: Leverages `watchdog` to monitor recursive directory changes with debouncing to collapse burst IDE saves.
   - `GitTracker`: Uses `GitPython` to poll the HEAD commit, extracting insertions, deletions, merges, and tags in real-time.
   - `SessionManager`: Handles graceful start, stop, and automated stale session recovery algorithms.
3. **Timeline Engine (`prometra/timeline`)**: Funnels disparate data sources into a unified `TimelineEventModel` sequence for chronological querying.
4. **Analyzer & Reports (`prometra/analyzer`, `prometra/reports`)**: Live queries the timeline sequence to formulate file language distributions, dependency risk metrics, and generate portable document artifacts.
