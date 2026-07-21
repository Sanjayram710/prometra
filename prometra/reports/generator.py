import json
import csv
import os
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, SessionModel

class ReportGenerator:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def _fetch_data(self, project_id: str):
        db = self.storage.get_session()
        try:
            sessions = db.query(SessionModel).filter_by(project_id=project_id).all()
            events = db.query(TimelineEventModel).order_by(TimelineEventModel.sequence).all()
            
            s_data = [{"session_id": s.session_id, "start": str(s.start_ts), "duration": s.duration_seconds} for s in sessions]
            e_data = [{"seq": e.sequence, "type": e.normalized_event_type, "time": str(e.timestamp), "summary": e.summary} for e in events]
            
            return {"project_id": project_id, "sessions": s_data, "timeline": e_data}
        finally:
            db.close()

    def generate_json(self, project_id: str, output_path: str):
        data = self._fetch_data(project_id)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return output_path

    def generate_markdown(self, project_id: str, output_path: str):
        data = self._fetch_data(project_id)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(f"# Prometra Report for {project_id}\n\n")
            f.write("## Sessions\n")
            for s in data["sessions"]:
                f.write(f"- Session {s['session_id']}: Started {s['start']}, Duration: {s['duration']}s\n")
            f.write("\n## Timeline\n")
            for e in data["timeline"]:
                f.write(f"- {e['time']} [{e['type'].upper()}]: {e['summary']}\n")
        return output_path

    def generate_csv(self, project_id: str, output_path: str):
        data = self._fetch_data(project_id)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Sequence", "Time", "Type", "Summary"])
            for e in data["timeline"]:
                writer.writerow([e["seq"], e["time"], e["type"], e["summary"]])
        return output_path

    def generate_html(self, project_id: str, output_path: str):
        data = self._fetch_data(project_id)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            f.write("<html><body>")
            f.write(f"<h1>Prometra Report for {project_id}</h1>")
            f.write("<h2>Sessions</h2><ul>")
            for s in data["sessions"]:
                f.write(f"<li>Session {s['session_id']}: Started {s['start']}</li>")
            f.write("</ul><h2>Timeline</h2><table border='1'><tr><th>Time</th><th>Type</th><th>Summary</th></tr>")
            for e in data["timeline"]:
                f.write(f"<tr><td>{e['time']}</td><td>{e['type']}</td><td>{e['summary']}</td></tr>")
            f.write("</table></body></html>")
        return output_path
