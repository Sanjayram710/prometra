from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AiUsageStats(BaseModel):
    total_prompts: int = 0
    total_tool_calls: int = 0
    estimated_tokens: int = 0
    estimated_cost: float = 0.0
    most_used_model: str = "claude-3-5-sonnet"
    response_frequency_min: float = 0.0

class ProductivityScore(BaseModel):
    score: int = 0  # 0 to 100
    stars: str = "☆☆☆☆☆"  # e.g. ★★★★☆
    focus_time_score: int = 0
    commit_frequency_score: int = 0
    ai_usage_score: int = 0
    consistency_score: int = 0
    completion_score: int = 0
    breakdown: Dict[str, Any] = Field(default_factory=dict)

class CodingPattern(BaseModel):
    name: str
    category: str  # e.g., 'session_length', 'context_switch', 'refactor', 'doc'
    description: str
    severity: str = "info"  # 'info', 'warning', 'positive'

class Recommendation(BaseModel):
    title: str
    description: str
    action_item: str
    priority: str = "medium"  # 'low', 'medium', 'high'

class SessionClassification(BaseModel):
    primary_category: str  # 'Feature Development', 'Bug Fix', 'Refactoring', 'Documentation', 'Research', 'Testing', 'Maintenance'
    confidence: float = 1.0
    secondary_categories: List[str] = Field(default_factory=list)

class SessionSummary(BaseModel):
    session_id: str
    duration_minutes: float = 0.0
    duration_hours: float = 0.0
    total_events: int = 0
    files_created: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    git_commits: int = 0
    ai_prompts: int = 0
    most_active_period: str = "N/A"
    top_edited_files: List[Dict[str, Any]] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    coding_intensity: str = "Moderate"  # 'Low', 'Moderate', 'High', 'Very High'

class InsightsResult(BaseModel):
    summary: SessionSummary
    classification: SessionClassification
    productivity: ProductivityScore
    ai_usage: AiUsageStats
    patterns: List[CodingPattern] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
