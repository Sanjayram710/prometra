from typing import List, Dict, Any
from prometra.intelligence.models import CodingPattern

class PatternDetector:
    """Detects behavioral patterns from session event history."""

    @staticmethod
    def detect_patterns(
        duration_minutes: float,
        files_created: int,
        files_modified: int,
        top_files: List[Dict[str, Any]],
        commit_messages: List[str],
        prompts: List[str],
        context_switches: int = 0
    ) -> List[CodingPattern]:
        patterns: List[CodingPattern] = []

        # 1. Long Coding Session
        if duration_minutes > 120:
            patterns.append(CodingPattern(
                name="Long Coding Session",
                category="session_length",
                description=f"Session extended for {duration_minutes:.0f} minutes continuous work.",
                severity="warning"
            ))

        # 2. Frequent Context Switching
        if context_switches > 4:
            patterns.append(CodingPattern(
                name="Frequent Context Switching",
                category="context_switch",
                description=f"Switched context between {context_switches} distinct module areas.",
                severity="warning"
            ))

        # 3. Repeated File Edits
        for item in top_files:
            path = item.get("path", "")
            count = item.get("count", 0)
            if count >= 8:
                patterns.append(CodingPattern(
                    name="Repeated File Churn",
                    category="file_churn",
                    description=f"File '{path}' was edited {count} times in a single session.",
                    severity="warning"
                ))
                break

        # 4. Large Refactors
        if files_modified >= 5 and files_created == 0:
            patterns.append(CodingPattern(
                name="Large Code Refactor",
                category="refactor",
                description=f"Modified {files_modified} existing files without creating new modules.",
                severity="info"
            ))

        # 5. Documentation-Heavy Session
        doc_count = sum(1 for item in top_files if item.get("path", "").endswith((".md", ".txt", ".rst")))
        if doc_count > 0 or any("doc" in msg.lower() for msg in commit_messages + prompts):
            patterns.append(CodingPattern(
                name="Documentation-Heavy Session",
                category="doc",
                description="High concentration of documentation updates.",
                severity="positive"
            ))

        # 6. Bug-Fix Activity
        if any(w in msg.lower() for msg in commit_messages + prompts for w in ("fix", "bug", "issue", "patch", "error")):
            patterns.append(CodingPattern(
                name="Bug-Fix Activity",
                category="bug_fix",
                description="Session focused on resolving bugs or error diagnostics.",
                severity="info"
            ))

        # 7. Feature Development Activity
        if files_created > 0 or any(w in msg.lower() for w in commit_messages + prompts for w in ("feat", "add", "feature", "create")):
            patterns.append(CodingPattern(
                name="Feature Development",
                category="feature",
                description=f"Added new features and created {files_created} new files.",
                severity="positive"
            ))

        return patterns
