import json
import os
from prometra.storage.sqlite import SQLiteStorage

class ReportGenerator:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def generate_json(self, project_id: str, output_path: str):
        report_data = {
            "project_id": project_id,
            "summary": "Project report generation V1"
        }
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
        return output_path

    def generate_markdown(self, project_id: str, output_path: str):
        md_content = f"# Prometra Report\n\n**Project ID:** {project_id}\n\nThis is an auto-generated report for V1."
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(md_content)
        return output_path
