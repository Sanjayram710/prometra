import csv
import json
import io
import os
from typing import List, Dict, Any
from prometra.storage.models import TimelineEventModel

class TimelineFormatter:
    """Formats timeline events for export and output representations."""

    @staticmethod
    def event_to_dict(e: TimelineEventModel) -> Dict[str, Any]:
        return {
            "id": e.id,
            "timestamp": str(e.timestamp) if e.timestamp else "",
            "normalized_event_type": e.normalized_event_type or "",
            "source": e.source or "",
            "actor_tool": e.actor_tool or "",
            "session_id": e.session_id or "",
            "summary": e.summary or "",
            "sequence": e.sequence
        }

    @classmethod
    def to_json(cls, events: List[TimelineEventModel]) -> str:
        data = [cls.event_to_dict(e) for e in events]
        return json.dumps(data, indent=2)

    @classmethod
    def to_csv(cls, events: List[TimelineEventModel]) -> str:
        output = io.StringIO()
        fieldnames = ["Timestamp", "Category", "Source", "Description", "Session", "Connector"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for e in events:
            writer.writerow({
                "Timestamp": str(e.timestamp) if e.timestamp else "",
                "Category": e.normalized_event_type or "",
                "Source": e.source or "",
                "Description": e.summary or "",
                "Session": e.session_id or "",
                "Connector": e.actor_tool or e.source or ""
            })
        return output.getvalue()

    @classmethod
    def to_markdown(cls, events: List[TimelineEventModel]) -> str:
        lines = ["# Prometra Timeline Export\n"]
        lines.append("| Timestamp | Category | Source | Description | Session | Connector |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for e in events:
            ts = str(e.timestamp) if e.timestamp else ""
            cat = e.normalized_event_type or ""
            src = e.source or ""
            desc = (e.summary or "").replace("|", "\\|")
            sess = e.session_id or ""
            conn = e.actor_tool or e.source or ""
            lines.append(f"| {ts} | {cat} | {src} | {desc} | {sess} | {conn} |")
        return "\n".join(lines)

    @classmethod
    def export_to_file(cls, events: List[TimelineEventModel], export_path: str) -> str:
        """Export timeline events to file based on file extension (.md, .csv, .json)."""
        ext = os.path.splitext(export_path)[1].lower()
        if ext == ".json":
            content = cls.to_json(events)
        elif ext == ".csv":
            content = cls.to_csv(events)
        elif ext == ".md" or ext == ".markdown":
            content = cls.to_markdown(events)
        else:
            # Default to Markdown if unknown extension
            content = cls.to_markdown(events)
            
        parent_dir = os.path.dirname(export_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return export_path
