from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import SessionModel, TimelineEventModel

class HealthAnalyzer:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def analyze(self, project_id: str):
        db = self.storage.get_session()
        try:
            total_sessions = db.query(SessionModel).filter_by(project_id=project_id).count()
            
            fs_events = db.query(TimelineEventModel).filter_by(normalized_event_type="filesystem").count()
            git_events = db.query(TimelineEventModel).filter_by(normalized_event_type="git").count()
            
            score = 100.0
            findings = []
            
            if total_sessions == 0:
                score -= 50
                findings.append("No active or past sessions found. Start tracking!")
            else:
                findings.append(f"Tracked {total_sessions} sessions.")
                
            if fs_events == 0 and git_events == 0:
                score -= 20
                findings.append("No file or git activity detected yet.")
            else:
                findings.append(f"Detected {fs_events} file changes and {git_events} git events.")
                
            return {
                "status": "success",
                "score": max(0.0, score),
                "findings": findings,
                "severity": "low" if score > 80 else "medium",
                "recommendation": "Maintain regular tracking."
            }
        finally:
            db.close()
