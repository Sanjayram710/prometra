from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class FileVersion:
    """Represents a specific tracked version of a file from event history."""
    event_id: int
    file_path: str
    content: str
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None

@dataclass
class DiffResult:
    """Data model representing the computed diff between two file versions."""
    file: str
    event_from: int
    event_to: int
    session_id: Optional[str]
    timestamp_from: Optional[str]
    timestamp_to: Optional[str]
    added_lines: int
    removed_lines: int
    modified_lines: int
    diff: str
    from_content: Optional[str] = None
    to_content: Optional[str] = None

@dataclass
class DiffOptions:
    """CLI query options for file diff generation."""
    file_path: str
    session_id: Optional[str] = None
    from_event: Optional[int] = None
    to_event: Optional[int] = None
    latest: bool = False
    json_output: bool = False
    markdown_output: bool = False
    context: int = 3
