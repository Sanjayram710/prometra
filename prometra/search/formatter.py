from prometra.search.models import SearchResultSet

class SearchFormatter:
    """Formats SearchResultSet into JSON and Markdown representations."""

    @classmethod
    def to_json(cls, result_set: SearchResultSet) -> str:
        return result_set.model_dump_json(indent=2)

    @classmethod
    def to_markdown(cls, result_set: SearchResultSet) -> str:
        lines = [
            "# Prometra Search Results\n",
            f"**Query:** `{result_set.query}` | **Results:** `{result_set.total_results}` | **Latency:** `{result_set.execution_time_ms} ms`\n"
        ]

        if result_set.applied_filters:
            lines.append("### Applied Filters")
            for k, v in result_set.applied_filters.items():
                lines.append(f"- **{k}:** `{v}`")
            lines.append("")

        lines.append("---")
        lines.append("\n| Timestamp | Category | Source | Session ID | Summary |")
        lines.append("| --- | --- | --- | --- | --- |")

        if result_set.results:
            for item in result_set.results:
                ts_str = str(item.timestamp).split(" ")[-1][:8] if item.timestamp and " " in str(item.timestamp) else str(item.timestamp or "")
                sess_short = item.session_id[:8] if item.session_id else "none"
                cat = item.category or "Event"
                src = item.source or "system"
                summary = item.summary.replace("|", "\\|")
                lines.append(f"| {ts_str} | {cat} | {src} | {sess_short} | {summary} |")
        else:
            lines.append("| - | - | - | - | No matching search results found. |")

        return "\n".join(lines)
