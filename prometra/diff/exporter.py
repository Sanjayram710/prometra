from prometra.diff.models import DiffResult
from prometra.diff.formatter import DiffFormatter

class DiffExporter:
    """Exporter for saving or outputting DiffResult in various formats."""

    @staticmethod
    def to_json(result: DiffResult, indent: int = 2) -> str:
        """Export DiffResult as JSON string."""
        return DiffFormatter.to_json(result, indent=indent)

    @staticmethod
    def to_markdown(result: DiffResult) -> str:
        """Export DiffResult as Markdown string."""
        return DiffFormatter.to_markdown(result)
