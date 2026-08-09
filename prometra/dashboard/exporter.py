import os

from prometra.dashboard.formatter import DashboardFormatter
from prometra.dashboard.metrics import DashboardMetrics


class DashboardExporter:
    """Exports analytics dashboard metrics to file (.md, .json)."""

    @classmethod
    def export(cls, metrics: DashboardMetrics, export_path: str) -> str:
        ext = os.path.splitext(export_path)[1].lower()
        if ext == ".json":
            content = DashboardFormatter.to_json(metrics)
        else:
            content = DashboardFormatter.to_markdown(metrics)

        parent_dir = os.path.dirname(export_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)

        return export_path
