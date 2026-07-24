import pytest
import os
import json
import tempfile
import datetime
from typer.testing import CliRunner

from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, AiEventModel, GitEventModel, SessionModel
from prometra.intelligence.models import (
    AiUsageStats,
    ProductivityScore,
    CodingPattern,
    Recommendation,
    SessionClassification,
    SessionSummary,
    InsightsResult,
)
from prometra.intelligence.scorer import ProductivityScorer
from prometra.intelligence.patterns import PatternDetector
from prometra.intelligence.productivity import SessionClassifier
from prometra.intelligence.recommendations import RecommendationEngine
from prometra.intelligence.summaries import SummaryBuilder
from prometra.intelligence.analyzer import IntelligenceAnalyzer
from prometra.tui.views.insights_view import InsightsView
from prometra.core.time import utcnow

runner = CliRunner()

@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_intel.db")
        storage = SQLiteStorage(db_path)
        try:
            yield storage
        finally:
            storage.engine.dispose()

@pytest.fixture
def populated_intel_db(temp_storage):
    db = temp_storage.get_session()
    
    s1 = SessionModel(
        session_id="intel-sess-1",
        project_id="intel_proj",
        start_ts=utcnow() - datetime.timedelta(hours=2),
        duration_seconds=3600,
        project_path="/app",
        working_directory="/app",
        status="completed"
    )
    db.add(s1)

    # Timeline events
    tl1 = TimelineEventModel(
        normalized_event_type="filesystem",
        timestamp=utcnow() - datetime.timedelta(hours=2),
        sequence=1,
        source="filesystem",
        session_id="intel-sess-1",
        summary="File created: main.py"
    )
    tl2 = TimelineEventModel(
        normalized_event_type="ai_prompt",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=45),
        sequence=2,
        source="claude",
        session_id="intel-sess-1",
        summary="Prompt: Add user feature"
    )
    tl3 = TimelineEventModel(
        normalized_event_type="git",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=30),
        sequence=3,
        source="git",
        session_id="intel-sess-1",
        summary="git commit: feat: add new feature"
    )
    db.add_all([tl1, tl2, tl3])

    # Filesystem events
    fs1 = FilesystemEventModel(
        event_id="fs-1",
        session_id="intel-sess-1",
        project_id="intel_proj",
        timestamp=utcnow() - datetime.timedelta(hours=2),
        operation="created",
        path="main.py",
        normalized_relative_path="main.py"
    )
    fs2 = FilesystemEventModel(
        event_id="fs-2",
        session_id="intel-sess-1",
        project_id="intel_proj",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=50),
        operation="modified",
        path="main.py",
        normalized_relative_path="main.py"
    )
    db.add_all([fs1, fs2])

    # AI events
    ai1 = AiEventModel(
        event_id="ai-1",
        session_id="intel-sess-1",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=45),
        event_type="UserPrompt",
        connector="claude",
        description="Prompt: Add user feature"
    )
    db.add(ai1)

    # Git events
    git1 = GitEventModel(
        event_id="git-1",
        repository="/app",
        branch="main",
        timestamp=utcnow() - datetime.timedelta(hours=1, minutes=30),
        commit_id="abc1234",
        message="feat: add new feature",
        author="Dev"
    )
    db.add(git1)

    db.commit()
    db.close()
    return temp_storage

def test_productivity_scorer():
    score_res = ProductivityScorer.calculate_score(
        duration_minutes=45.0,
        total_events=20,
        files_modified=5,
        commits=3,
        ai_prompts=5,
        context_switches=1
    )
    assert 0 <= score_res.score <= 100
    assert len(score_res.stars) == 5
    assert "★" in score_res.stars
    assert "focus_time" in score_res.breakdown

def test_pattern_detector():
    patterns = PatternDetector.detect_patterns(
        duration_minutes=150.0,
        files_created=2,
        files_modified=8,
        top_files=[{"path": "app.py", "count": 10}],
        commit_messages=["fix: resolve crash"],
        prompts=["fix bug in main"],
        context_switches=6
    )
    names = [p.name for p in patterns]
    assert "Long Coding Session" in names
    assert "Frequent Context Switching" in names
    assert "Repeated File Churn" in names
    assert "Bug-Fix Activity" in names

def test_session_classifier():
    cls_feat = SessionClassifier.classify_session(
        files_created=3,
        files_modified=5,
        commit_messages=["feat: add auth"],
        prompts=["build authentication endpoint"],
        file_paths=["auth.py", "user.py"]
    )
    assert cls_feat.primary_category == "Feature Development"
    assert cls_feat.confidence > 0.5

    cls_bug = SessionClassifier.classify_session(
        files_created=0,
        files_modified=2,
        commit_messages=["fix: resolve null crash"],
        prompts=["fix exception in handler"],
        file_paths=["handler.py"]
    )
    assert cls_bug.primary_category == "Bug Fix"

def test_recommendation_engine():
    patterns = [CodingPattern(name="Frequent Context Switching", category="context_switch", description="Switched context")]
    top_files = [{"path": "core.py", "count": 12}]

    recs = RecommendationEngine.generate_recommendations(
        duration_minutes=140.0,
        files_created=3,
        files_modified=5,
        commits=0,
        patterns=patterns,
        top_files=top_files
    )
    titles = [r.title for r in recs]
    assert "Frequent Commit Practice" in titles
    assert "Rest & Break Reminder" in titles
    assert "File Refactoring Opportunity" in titles

def test_summary_builder(populated_intel_db):
    builder = SummaryBuilder(populated_intel_db)
    summary, ai_usage, commits, prompts, file_paths = builder.build_summary(session_id="intel-sess-1")

    assert summary.session_id == "intel-sess-1"
    assert summary.files_created == 1
    assert summary.files_modified == 1
    assert summary.git_commits == 1
    assert summary.ai_prompts >= 1
    assert "Python" in summary.languages
    assert ai_usage.total_prompts >= 1

def test_intelligence_analyzer_and_exporters(populated_intel_db):
    analyzer = IntelligenceAnalyzer(populated_intel_db)
    res = analyzer.analyze_session(session_id="intel-sess-1")

    assert res.summary.session_id == "intel-sess-1"
    assert res.productivity.score > 0
    assert res.classification.primary_category is not None

    json_str = analyzer.to_json(res)
    data = json.loads(json_str)
    assert data["summary"]["session_id"] == "intel-sess-1"

    md_str = analyzer.to_markdown(res)
    assert "# Prometra AI Session Intelligence Report" in md_str
    assert "Productivity Score" in md_str

    csv_str = analyzer.to_csv(res)
    assert "Session ID" in csv_str
    assert "intel-sess-1" in csv_str

def test_insights_tui_view(populated_intel_db):
    view = InsightsView(storage=populated_intel_db)
    view.refresh_data()
    rendered = view.render()
    assert rendered is not None

def test_cli_insights(monkeypatch, populated_intel_db):
    monkeypatch.setattr("prometra.cli.commands.get_storage", lambda: populated_intel_db)

    # 1. Help
    res_help = runner.invoke(app, ["insights", "--help"])
    assert res_help.exit_code == 0
    assert "insights" in res_help.stdout.lower() or "session" in res_help.stdout.lower()

    # 2. Rich default panel output
    res_default = runner.invoke(app, ["insights", "--session", "intel-sess-1"])
    assert res_default.exit_code == 0
    assert "Prometra AI Session Intelligence" in res_default.stdout

    # 3. JSON output
    res_json = runner.invoke(app, ["insights", "--session", "intel-sess-1", "--json"])
    assert res_json.exit_code == 0
    assert '"session_id": "intel-sess-1"' in res_json.stdout

    # 4. Markdown output
    res_md = runner.invoke(app, ["insights", "--session", "intel-sess-1", "--markdown"])
    assert res_md.exit_code == 0
    assert "# Prometra AI Session Intelligence Report" in res_md.stdout

    # 5. CSV output
    res_csv = runner.invoke(app, ["insights", "--session", "intel-sess-1", "--csv"])
    assert res_csv.exit_code == 0
    assert "intel-sess-1" in res_csv.stdout
