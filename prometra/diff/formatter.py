import json
from typing import Dict, Any
from prometra.diff.models import DiffResult

class DiffFormatter:
    """Formatter for converting DiffResult into Markdown or JSON outputs."""

    @staticmethod
    def to_dict(result: DiffResult) -> Dict[str, Any]:
        """Convert DiffResult to exact JSON dictionary structure."""
        return {
            "file": result.file,
            "event_from": result.event_from,
            "event_to": result.event_to,
            "session_id": result.session_id,
            "timestamp_from": result.timestamp_from,
            "timestamp_to": result.timestamp_to,
            "added_lines": result.added_lines,
            "removed_lines": result.removed_lines,
            "modified_lines": result.modified_lines,
            "diff": result.diff
        }

    @staticmethod
    def to_json(result: DiffResult, indent: int = 2) -> str:
        """Format DiffResult as JSON string."""
        return json.dumps(DiffFormatter.to_dict(result), indent=indent)

    @staticmethod
    def to_markdown(result: DiffResult) -> str:
        """Format DiffResult as Markdown document."""
        lines = [
            "# File Diff",
            "",
            f"- **File:** `{result.file}`",
            f"- **Compared:** Event {result.event_from} → Event {result.event_to}",
            f"- **Session ID:** `{result.session_id or 'N/A'}`",
            f"- **Timestamp From:** `{result.timestamp_from or 'N/A'}`",
            f"- **Timestamp To:** `{result.timestamp_to or 'N/A'}`",
            f"- **Stats:** +{result.added_lines} added, -{result.removed_lines} removed, ~{result.modified_lines} modified",
            "",
            "```diff",
            result.diff.strip() if result.diff else "# No changes detected",
            "```",
            ""
        ]
        return "\n".join(lines)
