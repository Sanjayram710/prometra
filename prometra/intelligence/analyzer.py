import csv
import io

from prometra.intelligence.models import InsightsResult
from prometra.intelligence.patterns import PatternDetector
from prometra.intelligence.productivity import SessionClassifier
from prometra.intelligence.recommendations import RecommendationEngine
from prometra.intelligence.scorer import ProductivityScorer
from prometra.intelligence.summaries import SummaryBuilder
from prometra.storage.sqlite import SQLiteStorage


class IntelligenceAnalyzer:
    """Main analyzer engine coordinating session summary, classification, scoring, patterns, and recommendations."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def analyze_session(self, session_id: str | None = None) -> InsightsResult:
        """Run full session intelligence analysis."""
        summary_builder = SummaryBuilder(self.storage)
        summary, ai_usage, commit_messages, prompts_text, file_paths = (
            summary_builder.build_summary(session_id=session_id)
        )

        # 1. Session Classification
        classification = SessionClassifier.classify_session(
            files_created=summary.files_created,
            files_modified=summary.files_modified,
            commit_messages=commit_messages,
            prompts=prompts_text,
            file_paths=file_paths,
        )

        # 2. Context switch count heuristic
        dirs = set()
        for p in file_paths:
            parts = p.replace("\\", "/").split("/")
            if len(parts) > 1:
                dirs.add(parts[0])
        context_switches = len(dirs)

        # 3. Pattern Detection
        patterns = PatternDetector.detect_patterns(
            duration_minutes=summary.duration_minutes,
            files_created=summary.files_created,
            files_modified=summary.files_modified,
            top_files=summary.top_edited_files,
            commit_messages=commit_messages,
            prompts=prompts_text,
            context_switches=context_switches,
        )

        # 4. Productivity Scoring
        productivity = ProductivityScorer.calculate_score(
            duration_minutes=summary.duration_minutes,
            total_events=summary.total_events,
            files_modified=summary.files_modified,
            commits=summary.git_commits,
            ai_prompts=ai_usage.total_prompts,
            context_switches=context_switches,
        )

        # 5. Recommendations
        recommendations = RecommendationEngine.generate_recommendations(
            duration_minutes=summary.duration_minutes,
            files_created=summary.files_created,
            files_modified=summary.files_modified,
            commits=summary.git_commits,
            patterns=patterns,
            top_files=summary.top_edited_files,
        )

        return InsightsResult(
            summary=summary,
            classification=classification,
            productivity=productivity,
            ai_usage=ai_usage,
            patterns=patterns,
            recommendations=recommendations,
        )

    @staticmethod
    def to_json(result: InsightsResult) -> str:
        """Serialize InsightsResult to JSON string."""
        return result.model_dump_json(indent=2)

    @staticmethod
    def to_markdown(result: InsightsResult) -> str:
        """Serialize InsightsResult to clean Markdown report."""
        s = result.summary
        c = result.classification
        p = result.productivity
        ai = result.ai_usage

        md = []
        md.append("# Prometra AI Session Intelligence Report")
        md.append(
            f"**Session ID:** `{s.session_id}` | **Category:** `{c.primary_category}` | **Productivity Score:** `{p.score} / 100` ({p.stars})\n"
        )

        md.append("## 📊 Session Overview Summary")
        md.append(
            f"- **Duration:** {s.duration_minutes:.1f} mins ({s.duration_hours:.2f} hrs)"
        )
        md.append(f"- **Total Events Recorded:** {s.total_events}")
        md.append(
            f"- **Files Modified / Created / Deleted:** {s.files_modified} / {s.files_created} / {s.files_deleted}"
        )
        md.append(f"- **Git Commits:** {s.git_commits}")
        md.append(f"- **AI Prompts Used:** {s.ai_prompts}")
        md.append(f"- **Languages Worked On:** {', '.join(s.languages)}")
        md.append(f"- **Coding Intensity:** {s.coding_intensity}")
        md.append(f"- **Most Active Coding Period:** {s.most_active_period}\n")

        md.append("## 🤖 AI Usage & Synergy Analytics")
        md.append(f"- **Total Prompts:** {ai.total_prompts}")
        md.append(f"- **Total Tool Calls:** {ai.total_tool_calls}")
        md.append(f"- **Estimated Tokens:** {ai.estimated_tokens:,}")
        md.append(f"- **Estimated Cost:** ${ai.estimated_cost:.3f}")
        md.append(f"- **Primary AI Model:** `{ai.most_used_model}`\n")

        if result.patterns:
            md.append("## 🔍 Detected Coding Patterns")
            for pat in result.patterns:
                md.append(f"- **[{pat.name}]** (`{pat.severity}`): {pat.description}")
            md.append("")

        if result.recommendations:
            md.append("## 💡 Actionable Developer Recommendations")
            for rec in result.recommendations:
                md.append(f"### {rec.title} (`{rec.priority.upper()}`)")
                md.append(f"{rec.description}")
                md.append(f"> **Action Item:** {rec.action_item}\n")

        return "\n".join(md)

    @staticmethod
    def to_csv(result: InsightsResult) -> str:
        """Serialize InsightsResult to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Category", "Metric", "Value"])
        s = result.summary
        c = result.classification
        p = result.productivity
        ai = result.ai_usage

        writer.writerow(["Summary", "Session ID", s.session_id])
        writer.writerow(["Summary", "Primary Category", c.primary_category])
        writer.writerow(["Summary", "Productivity Score", p.score])
        writer.writerow(["Summary", "Stars", p.stars])
        writer.writerow(["Summary", "Duration Minutes", s.duration_minutes])
        writer.writerow(["Summary", "Total Events", s.total_events])
        writer.writerow(["Summary", "Files Modified", s.files_modified])
        writer.writerow(["Summary", "Files Created", s.files_created])
        writer.writerow(["Summary", "Git Commits", s.git_commits])
        writer.writerow(["AI Usage", "Prompts Count", ai.total_prompts])
        writer.writerow(["AI Usage", "Estimated Cost USD", ai.estimated_cost])

        return output.getvalue()
