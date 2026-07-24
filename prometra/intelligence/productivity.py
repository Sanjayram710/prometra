from typing import List, Dict, Any
from prometra.intelligence.models import SessionClassification

class SessionClassifier:
    """Classifies development sessions based on file operations, git messages, and AI prompt intent."""

    @staticmethod
    def classify_session(
        files_created: int,
        files_modified: int,
        commit_messages: List[str],
        prompts: List[str],
        file_paths: List[str]
    ) -> SessionClassification:
        scores: Dict[str, float] = {
            "Feature Development": 0.0,
            "Bug Fix": 0.0,
            "Refactoring": 0.0,
            "Documentation": 0.0,
            "Research": 0.0,
            "Testing": 0.0,
            "Maintenance": 0.0,
        }

        all_text = " ".join(commit_messages + prompts).lower()
        all_paths = " ".join(file_paths).lower()

        # Check keyword intent
        if any(w in all_text for w in ("feat", "add", "implement", "build", "create", "new")):
            scores["Feature Development"] += 3.0
        if any(w in all_text for w in ("fix", "bug", "issue", "resolve", "patch", "error", "exception")):
            scores["Bug Fix"] += 3.0
        if any(w in all_text for w in ("refactor", "clean", "structure", "move", "rename", "format")):
            scores["Refactoring"] += 3.0
        if any(w in all_text for w in ("doc", "readme", "comment", "docs", "changelog")):
            scores["Documentation"] += 3.0
        if any(w in all_text for w in ("test", "pytest", "mock", "spec", "coverage")):
            scores["Testing"] += 3.0
        if any(w in all_text for w in ("why", "how", "search", "explain", "investigate", "explore")):
            scores["Research"] += 2.0

        # Check structural file indicators
        if files_created > 0:
            scores["Feature Development"] += files_created * 1.5

        if any("test" in p for p in file_paths):
            scores["Testing"] += 2.0

        if any(p.endswith((".md", ".txt", ".rst")) for p in file_paths):
            scores["Documentation"] += 2.5

        if files_modified >= 4 and files_created == 0:
            scores["Refactoring"] += 2.0

        # Fallback to Maintenance if score is low
        top_cat = max(scores, key=scores.get)
        max_score = scores[top_cat]

        if max_score < 1.0:
            primary = "Maintenance"
            confidence = 0.6
        else:
            primary = top_cat
            confidence = min(0.98, round(0.5 + (max_score / 10.0), 2))

        # Secondary categories with score >= 2.0
        secondaries = [cat for cat, s in sorted(scores.items(), key=lambda x: x[1], reverse=True) if cat != primary and s >= 2.0]

        return SessionClassification(
            primary_category=primary,
            confidence=confidence,
            secondary_categories=secondaries
        )
