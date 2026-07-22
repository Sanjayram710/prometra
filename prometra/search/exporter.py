import os
from prometra.search.models import SearchResultSet
from prometra.search.formatter import SearchFormatter

class SearchExporter:
    """Exports search results to specified file formats (.md, .json)."""

    @classmethod
    def export(cls, result_set: SearchResultSet, export_path: str) -> str:
        ext = os.path.splitext(export_path)[1].lower()
        if ext == ".json":
            content = SearchFormatter.to_json(result_set)
        else:
            content = SearchFormatter.to_markdown(result_set)

        parent_dir = os.path.dirname(export_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)

        return export_path
