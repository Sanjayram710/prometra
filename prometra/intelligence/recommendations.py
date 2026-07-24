from typing import List, Dict, Any
from prometra.intelligence.models import Recommendation, CodingPattern

class RecommendationEngine:
    """Generates developer actionable recommendations based on session patterns and metrics."""

    @staticmethod
    def generate_recommendations(
        duration_minutes: float,
        files_created: int,
        files_modified: int,
        commits: int,
        patterns: List[CodingPattern],
        top_files: List[Dict[str, Any]]
    ) -> List[Recommendation]:
        recs: List[Recommendation] = []

        # 1. Commit Frequency
        if files_modified >= 3 and commits == 0:
            recs.append(Recommendation(
                title="Frequent Commit Practice",
                description="You modified 3+ files in this session without recording a Git commit.",
                action_item="Consider committing more frequently to create smaller, safer rollback points.",
                priority="high"
            ))

        # 2. Long Session / Break Recommendation
        if duration_minutes > 120:
            recs.append(Recommendation(
                title="Rest & Break Reminder",
                description=f"Long continuous coding session detected ({duration_minutes:.0f} minutes).",
                action_item="Long session detected—take a 10-15 minute break to maintain cognitive focus.",
                priority="medium"
            ))

        # 3. Repeated File Churn
        for item in top_files:
            path = item.get("path", "")
            count = item.get("count", 0)
            if count >= 8:
                recs.append(Recommendation(
                    title="File Refactoring Opportunity",
                    description=f"File '{path}' changed {count} times during this session.",
                    action_item=f"This file changed {count} times today. Consider breaking it into smaller modular components.",
                    priority="high"
                ))
                break

        # 4. Missing Documentation
        has_doc_update = any(item.get("path", "").endswith((".md", ".txt", ".rst")) for item in top_files)
        if files_created >= 2 and not has_doc_update:
            recs.append(Recommendation(
                title="Documentation Hygiene",
                description=f"Created {files_created} new source modules without updating project documentation.",
                action_item="Documentation is missing for new modules. Update README or docstrings.",
                priority="medium"
            ))

        # 5. High Context Switch Penalty
        if any(p.name == "Frequent Context Switching" for p in patterns):
            recs.append(Recommendation(
                title="Reduce Context Switching",
                description="Activity spans across multiple unrelated components.",
                action_item="High context switching reduced focus. Try working on one module component at a time.",
                priority="medium"
            ))

        # Default positive feedback if session is clean
        if not recs:
            recs.append(Recommendation(
                title="Optimal Workflow",
                description="Your coding session demonstrates clean focus, regular commits, and modular changes.",
                action_item="Keep up the great work!",
                priority="low"
            ))

        return recs
