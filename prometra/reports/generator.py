import json
import csv
import os
from prometra.core.time import utcnow
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, SessionModel
from prometra.analyzer.stats import StatsCalculator

class ReportGenerator:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.stats = StatsCalculator(storage)

    def _fetch_data(self, project_id: str):
        db = self.storage.get_session()
        try:
            sessions = db.query(SessionModel).filter_by(project_id=project_id).all()
            events = db.query(TimelineEventModel).order_by(TimelineEventModel.sequence).all()
            stats_data = self.stats.compute_project_stats(project_id)
            
            s_data = [{"session_id": s.session_id, "start": str(s.start_ts), "duration": s.duration_seconds, "warnings": s.warnings} for s in sessions]
            e_data = [{"seq": e.sequence, "type": e.normalized_event_type, "time": str(e.timestamp), "summary": e.summary} for e in events]
            
            fs_summary = {"total_events": stats_data["total_file_events"], "languages": stats_data["language_distribution"]}
            git_summary = {"total_commits_tracked": stats_data["total_git_events"]}
            
            return {
                "project_id": project_id,
                "generation_timestamp": str(utcnow()),
                "schema_version": "1.0",
                "statistics": stats_data,
                "filesystem_summary": fs_summary,
                "git_summary": git_summary,
                "sessions": s_data,
                "timeline": e_data,
                "warnings": [w for s in sessions if s.warnings for w in s.warnings]
            }
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
            f.write(f"**Generated:** {data['generation_timestamp']} (Schema v{data['schema_version']})\n\n")
            
            f.write("## Project Statistics\n")
            f.write(f"- Total Sessions: {data['statistics']['total_sessions']}\n")
            f.write(f"- Total File Events: {data['statistics']['total_file_events']}\n")
            f.write(f"- Total Git Events: {data['statistics']['total_git_events']}\n\n")
            
            if data['warnings']:
                f.write("## Warnings\n")
                for w in set(data['warnings']):
                    f.write(f"- {w}\n")
                f.write("\n")
                
            f.write("## Sessions\n")
            for s in data["sessions"]:
                f.write(f"- Session `{s['session_id']}`: Started {s['start']}, Duration: {s['duration']}s\n")
            
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
            f.write(f"<p><b>Generated:</b> {data['generation_timestamp']}</p>")
            f.write("<h2>Sessions</h2><ul>")
            for s in data["sessions"]:
                f.write(f"<li>Session {s['session_id']}: Started {s['start']}</li>")
            f.write("</ul><h2>Timeline</h2><table border='1'><tr><th>Time</th><th>Type</th><th>Summary</th></tr>")
            for e in data["timeline"]:
                f.write(f"<tr><td>{e['time']}</td><td>{e['type']}</td><td>{e['summary']}</td></tr>")
            f.write("</table></body></html>")
        return output_path
