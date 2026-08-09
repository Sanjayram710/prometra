import json
from typing import Any

from prometra.compare.models import CompareResult


class CompareFormatter:
    """Formatter for converting CompareResult into Markdown or JSON outputs."""

    @staticmethod
    def to_dict(result: CompareResult) -> dict[str, Any]:
        """Convert CompareResult to exact JSON dictionary structure."""
        return {
            "session_a": result.session_a,
            "session_b": result.session_b,
            "duration_difference": result.duration_difference,
            "files_created_difference": result.files_created_difference,
            "files_modified_difference": result.files_modified_difference,
            "files_deleted_difference": result.files_deleted_difference,
            "git_commit_difference": result.git_commit_difference,
            "ai_event_difference": result.ai_event_difference,
            "timeline_difference": result.timeline_difference,
        }

    @staticmethod
    def to_json(result: CompareResult, indent: int = 2) -> str:
        """Format CompareResult as JSON string."""
        return json.dumps(CompareFormatter.to_dict(result), indent=indent)

    @staticmethod
    def to_markdown(result: CompareResult) -> str:
        """Format CompareResult as Markdown document."""
        dur_sign = "+" if result.duration_seconds_difference >= 0 else ""
        files_mod_sign = "+" if result.files_modified_difference >= 0 else ""
        files_cr_sign = "+" if result.files_created_difference >= 0 else ""
        files_del_sign = "+" if result.files_deleted_difference >= 0 else ""
        git_sign = "+" if result.git_commit_difference >= 0 else ""
        ai_sign = "+" if result.ai_event_difference >= 0 else ""
        total_sign = "+" if result.total_events_difference >= 0 else ""

        lines = [
            "# Session Comparison",
            "",
            "## Summary Table",
            "",
            "| Metric | Session A (`"
            + str(result.session_a)
            + "`) | Session B (`"
            + str(result.session_b)
            + "`) | Difference |",
            "| :--- | :--- | :--- | :--- |",
            f"| **Duration** | {result.stats_a.duration_minutes} min | {result.stats_b.duration_minutes} min | {dur_sign}{result.stats_b.duration_minutes - result.stats_a.duration_minutes} min |",
            f"| **Files Created** | {result.stats_a.files_created} | {result.stats_b.files_created} | {files_cr_sign}{result.files_created_difference} |",
            f"| **Files Modified** | {result.stats_a.files_modified} | {result.stats_b.files_modified} | {files_mod_sign}{result.files_modified_difference} |",
            f"| **Files Deleted** | {result.stats_a.files_deleted} | {result.stats_b.files_deleted} | {files_del_sign}{result.files_deleted_difference} |",
            f"| **Git Commits** | {result.stats_a.git_commits} | {result.stats_b.git_commits} | {git_sign}{result.git_commit_difference} |",
            f"| **AI Events** | {result.stats_a.ai_events} | {result.stats_b.ai_events} | {ai_sign}{result.ai_event_difference} |",
            f"| **Total Events** | {result.stats_a.total_events} | {result.stats_b.total_events} | {total_sign}{result.total_events_difference} |",
            "",
            "## Timeline Comparison",
            "",
            f"- **Session A Total Events:** {result.stats_a.total_events}",
            f"- **Session B Total Events:** {result.stats_b.total_events}",
            f"- **Net Event Change:** {total_sign}{result.total_events_difference}",
            "",
            "### Event Types Distribution",
            "",
            "**Session A:**",
        ]

        if result.stats_a.event_type_distribution:
            for k, v in result.stats_a.event_type_distribution.items():
                lines.append(f"- `{k}`: {v}")
        else:
            lines.append("- None recorded")

        lines.extend(
            [
                "",
                "**Session B:**",
            ]
        )

        if result.stats_b.event_type_distribution:
            for k, v in result.stats_b.event_type_distribution.items():
                lines.append(f"- `{k}`: {v}")
        else:
            lines.append("- None recorded")

        lines.extend(
            [
                "",
                "## Statistics & Productivity",
                "",
                "| Metric | Session A | Session B |",
                "| :--- | :--- | :--- |",
                f"| **Events / Minute** | {result.stats_a.productivity_metrics.get('events_per_minute', 0)} | {result.stats_b.productivity_metrics.get('events_per_minute', 0)} |",
                f"| **Files Changed / Minute** | {result.stats_a.productivity_metrics.get('files_changed_per_minute', 0)} | {result.stats_b.productivity_metrics.get('files_changed_per_minute', 0)} |",
                f"| **Commits / Hour** | {result.stats_a.productivity_metrics.get('commits_per_hour', 0)} | {result.stats_b.productivity_metrics.get('commits_per_hour', 0)} |",
                "",
            ]
        )

        return "\n".join(lines)
