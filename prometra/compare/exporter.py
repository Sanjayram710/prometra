import os

from prometra.compare.formatter import CompareFormatter
from prometra.compare.models import CompareResult


class CompareExporter:
    """Exporter for saving or outputting CompareResult in various formats."""

    @staticmethod
    def to_json(result: CompareResult, indent: int = 2) -> str:
        """Export CompareResult as JSON string."""
        return CompareFormatter.to_json(result, indent=indent)

    @staticmethod
    def to_markdown(result: CompareResult) -> str:
        """Export CompareResult as Markdown string."""
        return CompareFormatter.to_markdown(result)

    @staticmethod
    def export_to_file(
        result: CompareResult, export_path: str, format_override: str | None = None
    ) -> str:
        """Save comparison output to specified file path."""
        # Determine format from extension if not specified
        ext = os.path.splitext(export_path)[1].lower()
        if format_override == "json" or ext == ".json":
            content = CompareFormatter.to_json(result)
        elif format_override == "markdown" or ext in (".md", ".markdown"):
            content = CompareFormatter.to_markdown(result)
        else:
            # Default to Markdown output for file export
            content = CompareFormatter.to_markdown(result)

        dir_name = os.path.dirname(export_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)

        return export_path
