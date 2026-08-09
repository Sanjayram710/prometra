import json

from prometra.dashboard.metrics import DashboardMetrics


class DashboardFormatter:
    """Formats DashboardMetrics into JSON and Markdown representations."""

    @classmethod
    def to_json(cls, metrics: DashboardMetrics) -> str:
        return json.dumps(metrics.model_dump(), indent=2)

    @classmethod
    def to_markdown(cls, metrics: DashboardMetrics) -> str:
        sess = metrics.sessions
        dur = sess.total_duration_seconds
        dur_str = (
            f"{dur // 3600}h {(dur % 3600) // 60}m {dur % 60}s"
            if dur >= 3600
            else f"{dur // 60}m {dur % 60}s"
        )

        long_dur = sess.longest_session_seconds
        long_str = f"{long_dur // 60}m" if long_dur >= 60 else f"{long_dur}s"

        avg_dur = sess.avg_session_length_seconds
        avg_str = f"{avg_dur // 60}m" if avg_dur >= 60 else f"{avg_dur}s"

        lines = [
            "# Prometra Analytics Dashboard\n",
            f"**Time Window:** `{metrics.filter_label}`\n",
            "---",
            "\n## 📊 Session & Overview Metrics",
            f"- **Total Sessions:** `{sess.total_sessions}`",
            f"- **Total Duration:** `{dur_str}`",
            f"- **Longest Session:** `{long_str}`",
            f"- **Average Length:** `{avg_str}`\n",
            "## 📝 Filesystem & Git",
            f"- **Files Created:** `{metrics.filesystem.files_created}`",
            f"- **Files Modified:** `{metrics.filesystem.files_modified}`",
            f"- **Files Deleted:** `{metrics.filesystem.files_deleted}`",
            f"- **Git Commits:** `{metrics.git.total_commits}` (`{metrics.git.commits_per_day}` commits/day)\n",
            "## 🤖 AI Interactions & Costs",
            f"- **AI Prompts:** `{metrics.ai.ai_prompts}`",
            f"- **AI Responses:** `{metrics.ai.ai_responses}`",
            f"- **Tool Calls:** `{metrics.ai.tool_calls}`",
            f"- **Errors / Retries:** `{metrics.ai.errors}` / `{metrics.ai.retries}`",
            f"- **Total Tokens:** `{metrics.ai.total_tokens}` (Prompt: `{metrics.ai.prompt_tokens}`, Completion: `{metrics.ai.completion_tokens}`)",
            f"- **Estimated Cost:** `${metrics.ai.estimated_cost:.4f}`",
            f"- **Connectors Used:** `{', '.join(metrics.ai.connectors_used) if metrics.ai.connectors_used else 'None'}`\n",
            "## 🏆 Top Edited Files",
        ]

        if metrics.filesystem.top_edited_files:
            for idx, tf in enumerate(metrics.filesystem.top_edited_files, start=1):
                lines.append(f"{idx}. `{tf.path}` — {tf.edits} edits")
        else:
            lines.append("- No file modifications recorded.")

        lines.append("\n## 🤖 Top AI Models")
        if metrics.ai.top_models:
            for idx, tm in enumerate(metrics.ai.top_models, start=1):
                lines.append(f"{idx}. `{tm.model_name}` — {tm.count} prompts")
        else:
            lines.append("- No AI model interactions recorded.")

        if metrics.activity.top_active_hours:
            hours_str = ", ".join(
                f"{h:02d}:00" for h in metrics.activity.top_active_hours
            )
            lines.append(
                f"\n## ⏰ Peak Activity Hours\n- Most active hours: `{hours_str}`"
            )

        return "\n".join(lines)
