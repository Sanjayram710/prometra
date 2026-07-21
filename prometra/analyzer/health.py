from prometra.storage.sqlite import SQLiteStorage
from prometra.analyzer.stats import StatsCalculator

class HealthAnalyzer:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.stats = StatsCalculator(storage)

    def analyze(self, project_id: str):
        stats = self.stats.compute_project_stats(project_id)
        
        score = 100.0
        findings = []
        
        if stats["total_sessions"] == 0:
            score -= 50
            findings.append("No active or past sessions found. Start tracking!")
        else:
            findings.append(f"Tracked {stats['total_sessions']} sessions.")
            
        if stats["total_file_events"] == 0 and stats["total_git_events"] == 0:
            score -= 20
            findings.append("No file or git activity detected yet.")
        else:
            findings.append(f"Detected {stats['total_file_events']} file changes and {stats['total_git_events']} git events.")
            
        if stats["dependency_changes"] > 10:
            findings.append("High volume of dependency changes detected. Risk of instability.")
            score -= 10
            
        return {
            "status": "success",
            "score": max(0.0, score),
            "findings": findings,
            "severity": "low" if score > 80 else "medium" if score > 50 else "high",
            "recommendation": "Maintain regular tracking and commit often."
        }
