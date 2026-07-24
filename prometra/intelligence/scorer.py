from typing import Dict, Any
from prometra.intelligence.models import ProductivityScore

class ProductivityScorer:
    """Calculates a normalized 0–100 productivity score and star rating for a session."""

    @staticmethod
    def calculate_score(
        duration_minutes: float,
        total_events: int,
        files_modified: int,
        commits: int,
        ai_prompts: int,
        context_switches: int = 0
    ) -> ProductivityScore:
        # 1. Focus Time Score (max 25 pts)
        if 20 <= duration_minutes <= 180:
            focus_score = 25
        elif duration_minutes < 20:
            focus_score = max(5, int(duration_minutes * 1.25))
        else:
            focus_score = max(10, 25 - int((duration_minutes - 180) / 10))

        # 2. Commit Frequency Score (max 25 pts)
        if commits >= 3:
            commit_score = 25
        elif commits == 2:
            commit_score = 20
        elif commits == 1:
            commit_score = 15
        else:
            commit_score = 8 if files_modified > 0 else 5

        # 3. AI Usage & Synergy Score (max 20 pts)
        if 1 <= ai_prompts <= 20:
            ai_score = 20
        elif ai_prompts > 20:
            ai_score = 15
        else:
            ai_score = 12

        # 4. Consistency & Context Switching Score (max 15 pts)
        switch_penalty = min(10, context_switches * 2)
        consistency_score = max(5, 15 - switch_penalty)

        # 5. Completion / Output Score (max 15 pts)
        if total_events > 5 or files_modified > 0:
            completion_score = 15
        else:
            completion_score = 5

        total = focus_score + commit_score + ai_score + consistency_score + completion_score
        final_score = max(0, min(100, total))

        # Star calculation (0-100 -> 0-5 stars)
        star_count = round((final_score / 100) * 5)
        stars_str = "★" * star_count + "☆" * (5 - star_count)

        return ProductivityScore(
            score=final_score,
            stars=stars_str,
            focus_time_score=focus_score,
            commit_frequency_score=commit_score,
            ai_usage_score=ai_score,
            consistency_score=consistency_score,
            completion_score=completion_score,
            breakdown={
                "focus_time": f"{focus_score}/25",
                "commit_freq": f"{commit_score}/25",
                "ai_synergy": f"{ai_score}/20",
                "consistency": f"{consistency_score}/15",
                "completion": f"{completion_score}/15",
            }
        )
