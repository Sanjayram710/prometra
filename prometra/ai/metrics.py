from typing import List, Dict, Any
from prometra.ai.events import AiEvent, TokenUsage, LatencyMeasured, ErrorOccurred, ToolInvocation

class AiMetricsAggregator:
    @staticmethod
    def aggregate(events: List[AiEvent]) -> Dict[str, Any]:
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_latency_ms = 0
        latency_count = 0
        errors_count = 0
        tool_counts = {}

        for event in events:
            if isinstance(event, TokenUsage):
                total_prompt_tokens += event.tokens.prompt_tokens
                total_completion_tokens += event.tokens.completion_tokens
            elif isinstance(event, LatencyMeasured):
                total_latency_ms += event.latency_ms
                latency_count += 1
            elif isinstance(event, ErrorOccurred):
                errors_count += 1
            elif isinstance(event, ToolInvocation):
                tool_name = event.tool.tool_name
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

        avg_latency = (total_latency_ms / latency_count) if latency_count > 0 else 0
        
        return {
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "average_latency_ms": avg_latency,
            "error_count": errors_count,
            "tool_invocation_frequencies": tool_counts
        }
