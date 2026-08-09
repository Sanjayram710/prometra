from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileVersion:
    """Represents a specific tracked version of a file from event history."""

    event_id: int
    file_path: str
    content: str
    timestamp: datetime | None = None
    session_id: str | None = None


@dataclass
class DiffResult:
    """Data model representing the computed diff between two file versions."""

    file: str
    event_from: int
    event_to: int
    session_id: str | None
    timestamp_from: str | None
    timestamp_to: str | None
    added_lines: int
    removed_lines: int
    modified_lines: int
    diff: str
    from_content: str | None = None
    to_content: str | None = None


@dataclass
class DiffOptions:
    """CLI query options for file diff generation."""

    file_path: str
    session_id: str | None = None
    from_event: int | None = None
    to_event: int | None = None
    latest: bool = False
    json_output: bool = False
    markdown_output: bool = False
    context: int = 3
