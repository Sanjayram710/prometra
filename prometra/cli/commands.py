import typer
import os
import time
from typing import Optional
from rich.console import Console
from prometra.storage.sqlite import SQLiteStorage
from prometra.tracker.session import SessionManager
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.filters import TimelineFilter
from prometra.timeline.formatter import TimelineFormatter
from prometra.timeline.renderer import TimelineRenderer
from prometra.replay.engine import ReplayEngine
from prometra.replay.player import ReplayPlayer
from prometra.replay.formatter import ReplayFormatter
from prometra.replay.exporter import ReplayExporter
from prometra.dashboard.engine import DashboardEngine
from prometra.dashboard.renderer import DashboardRenderer
from prometra.dashboard.formatter import DashboardFormatter
from prometra.dashboard.exporter import DashboardExporter
from prometra.search.engine import SearchEngine
from prometra.search.renderer import SearchRenderer
from prometra.search.formatter import SearchFormatter
from prometra.search.exporter import SearchExporter
from prometra.tracker.filesystem import FilesystemTracker
from prometra.tracker.git import GitTracker
from prometra.analyzer.health import HealthAnalyzer
from prometra.reports.generator import ReportGenerator

console = Console()

def get_storage():
    db_path = os.path.abspath(os.path.join(".prometra", "prometra.db"))
    return SQLiteStorage(db_path)

def init():
    """Initialize a Prometra project in the current repository."""
    if not os.path.exists(".prometra"):
        os.makedirs(".prometra")
        # Ensure DB is created
        get_storage()
        console.print("[green]Initialized empty Prometra project in .prometra/[/green]")
    else:
        console.print("[yellow]Prometra project already initialized.[/yellow]")

    if not os.path.exists(".prometraignore"):
        template = (
            "# Prometra Smart Ignore Rules\n"
            "# Add files or directories to exclude from timeline and analytics tracking\n\n"
            "build/\n"
            "dist/\n"
            "logs/\n"
            "data/\n"
            "*.csv\n"
            "*.zip\n"
        )
        with open(".prometraignore", "w", encoding="utf-8") as f:
            f.write(template)
        console.print("[green]Created .prometraignore file.[/green]")

def start():
    """Start session tracking for the current project."""
    if not os.path.exists(".prometra"):
        console.print("[red]Project not initialized. Run `prometra init` first.[/red]")
        return
        
    project_id = os.path.basename(os.path.abspath("."))
    project_path = os.path.abspath(".")
    storage = get_storage()
    sm = SessionManager(storage)
    timeline_engine = TimelineEngine(storage)
    
    session = sm.start_session(project_id=project_id, project_path=project_path, working_directory=project_path)
    console.print(f"[green]Started Prometra session: {session.session_id}[/green]")
    console.print("[blue]Tracking in background... Press Ctrl+C to stop.[/blue]")
    
    fs_tracker = FilesystemTracker(watch_dir=project_path, timeline_engine=timeline_engine, session_id=session.session_id, project_id=project_id)
    git_tracker = GitTracker(repo_path=project_path, timeline_engine=timeline_engine, session_id=session.session_id)
    
    fs_tracker.start()
    git_tracker.start()
    
    try:
        while True:
            # Check if another process stopped the session
            db = storage.get_session()
            from prometra.storage.models import SessionModel
            current_session = db.query(SessionModel).filter_by(session_id=session.session_id).first()
            status = current_session.status if current_session else "completed"
            db.close()
            
            if status != "active":
                break
            time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupt received. Stopping session...[/yellow]")
        sm.end_session(session.session_id)
    finally:
        fs_tracker.stop()
        git_tracker.stop()
        console.print("[green]Session stopped gracefully.[/green]")

def stop(session_id: str = typer.Option(None, help="Specific session ID to stop")):
    """Stop the active session gracefully."""
    storage = get_storage()
    sm = SessionManager(storage)
    
    if not session_id:
        # Find active session
        db = storage.get_session()
        from prometra.storage.models import SessionModel
        project_id = os.path.basename(os.path.abspath("."))
        active = db.query(SessionModel).filter_by(project_id=project_id, status="active").first()
        if active:
            session_id = active.session_id
        db.close()
        
    if session_id:
        sm.end_session(session_id)
        console.print(f"[green]Stopped session {session_id}.[/green]")
    else:
        console.print("[yellow]No active session found.[/yellow]")

def analyze():
    """Run incremental or full analysis."""
    project_id = os.path.basename(os.path.abspath("."))
    storage = get_storage()
    analyzer = HealthAnalyzer(storage)
    res = analyzer.analyze(project_id)
    console.print(f"[blue]Analysis Complete: Score {res['score']} - {res['findings'][0]}[/blue]")

def report():
    """Generate Markdown, HTML, JSON, and CSV reports."""
    project_id = os.path.basename(os.path.abspath("."))
    storage = get_storage()
    generator = ReportGenerator(storage)
    generator.generate_markdown(project_id, ".prometra/reports/report.md")
    generator.generate_json(project_id, ".prometra/reports/report.json")
    generator.generate_csv(project_id, ".prometra/reports/report.csv")
    generator.generate_html(project_id, ".prometra/reports/report.html")
    console.print("[green]Generated reports in .prometra/reports/[/green]")

def status():
    """Display current session and tracking status."""
    project_id = os.path.basename(os.path.abspath("."))
    storage = get_storage()
    db = storage.get_session()
    from prometra.storage.models import SessionModel, FilesystemEventModel, GitEventModel
    try:
        active = db.query(SessionModel).filter_by(project_id=project_id, status="active").first()
        if active:
            console.print(f"[green]Active session:[/green] {active.session_id}")
            console.print(f"Project: {project_id}")
            
            from prometra.tracker.git import GitTracker
            git_tracker = GitTracker(os.path.abspath("."), None, None)
            console.print(f"Git branch: {git_tracker.get_current_branch()}")
            console.print(f"SQLite path: {storage.db_path}")
            
            fs_count = db.query(FilesystemEventModel).filter_by(session_id=active.session_id).count()
            git_count = db.query(GitEventModel).filter_by(session_id=active.session_id).count()
            console.print(f"Files tracked in session: {fs_count}")
            console.print(f"Git events in session: {git_count}")
            
            from prometra.core.time import utcnow
            duration = int((utcnow() - active.start_ts).total_seconds())
            console.print(f"Session duration: {duration}s")
        else:
            console.print("[yellow]No active session.[/yellow]")
    finally:
        db.close()

def history(today: bool = typer.Option(False, "--today"), session_id: str = typer.Option(None, "--session"), json_out: bool = typer.Option(False, "--json")):
    """Show previous sessions and high-level events."""
    project_id = os.path.basename(os.path.abspath("."))
    storage = get_storage()
    db = storage.get_session()
    from prometra.storage.models import SessionModel
    try:
        query = db.query(SessionModel).filter_by(project_id=project_id)
        if session_id:
            query = query.filter_by(session_id=session_id)
            
        sessions = query.all()
        if json_out:
            import json
            console.print(json.dumps([{"session_id": s.session_id, "start": str(s.start_ts), "duration": s.duration_seconds} for s in sessions]))
        else:
            for s in sessions:
                console.print(f"Session: {s.session_id} - Duration: {s.duration_seconds}s - Status: {s.status}")
    finally:
        db.close()

def timeline(
    session_id: Optional[str] = typer.Option(None, "--session", help="Filter by session ID"),
    event_type: Optional[str] = typer.Option(None, "--type", help="Filter by event type (filesystem, git, ai, connector, session)"),
    connector: Optional[str] = typer.Option(None, "--connector", help="Filter by AI connector name (e.g. claude)"),
    search: Optional[str] = typer.Option(None, "--search", help="Search descriptions and metadata"),
    today: bool = typer.Option(False, "--today", help="Show today's events only"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Limit maximum events returned"),
    reverse: bool = typer.Option(False, "--reverse", help="Reverse chronological order"),
    group: Optional[str] = typer.Option(None, "--group", help="Group events (e.g., session)"),
    summary: bool = typer.Option(False, "--summary", help="Show summary metrics"),
    export: Optional[str] = typer.Option(None, "--export", help="Export timeline to file (.md, .csv, .json)"),
    json_out: bool = typer.Option(False, "--json", help="Output raw JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output raw Markdown"),
    checkpoints: bool = typer.Option(False, "--checkpoints", help="Include saved checkpoints in timeline view")
):
    """Display interactive chronological project history with filtering and export support."""
    storage = get_storage()

    if checkpoints:
        from prometra.timemachine.timeline import CheckpointTimeline
        from rich.table import Table
        from rich.panel import Panel

        cp_tl = CheckpointTimeline(storage)
        items = cp_tl.get_timeline_with_checkpoints(session_id=session_id)

        tbl = Table("Time", "Type", "Session", "Summary", expand=True)
        for item in items:
            t_str = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if item["timestamp"] else "N/A"
            t_style = "bold yellow" if item["type"] == "checkpoint" else "cyan"
            tbl.add_row(t_str, f"[{t_style}]{item['event_type']}[/{t_style}]", item["session_id"], item["summary"])

        console.print(Panel(tbl, title="📍 Timeline with Checkpoints", border_style="yellow"))
        return

    engine = TimelineEngine(storage)
    
    filters = TimelineFilter(
        session_id=session_id,
        event_type=event_type,
        connector=connector,
        search=search,
        today=today,
        limit=limit,
        reverse=reverse,
        group=group,
        summary=summary,
        export=export
    )
    
    renderer = TimelineRenderer(console)
    
    if export:
        file_path = engine.export_events(filters, export)
        console.print(f"[green]Exported timeline to {file_path}[/green]")
        return

    if summary:
        metrics = engine.get_summary(filters)
        renderer.render_summary(metrics)
        return

    if group and group.lower() == "session":
        grouped = engine.get_grouped(filters)
        renderer.render_grouped(grouped)
        return

    events = engine.query_events(filters)

    if json_out:
        console.print(TimelineFormatter.to_json(events))
    elif markdown_out:
        console.print(TimelineFormatter.to_markdown(events))
    else:
        renderer.render_table(events)

def replay(
    session_id: Optional[str] = typer.Option(None, "--session", help="Session ID to replay"),
    latest: bool = typer.Option(False, "--latest", help="Replay the most recent session"),
    speed: str = typer.Option("instant", "--speed", help="Playback speed (1x, 2x, 5x, 10x, instant)"),
    step: bool = typer.Option(False, "--step", help="Pause after every event (step mode)"),
    json_out: bool = typer.Option(False, "--json", help="Output replay as JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output replay as Markdown"),
    export: Optional[str] = typer.Option(None, "--export", help="Export replay to file (.md, .json)")
):
    """Reconstruct and replay an entire development session from recorded events."""
    storage = get_storage()
    engine = ReplayEngine(storage)

    target_session_id = engine.resolve_session_id(session_id=session_id, latest=latest)
    if not target_session_id:
        console.print("[yellow]No session found to replay.[/yellow]")
        return

    session_info = engine.get_session_info(target_session_id)
    events = engine.get_session_events(target_session_id)

    if export:
        file_path = ReplayExporter.export(session_info, events, export)
        console.print(f"[green]Exported session replay to {file_path}[/green]")
        return

    if json_out:
        console.print(ReplayFormatter.to_json(session_info, events))
        return

    if markdown_out:
        console.print(ReplayFormatter.to_markdown(session_info, events))
        return

    player = ReplayPlayer()
    player.play(events, session_info, speed=speed, step=step)

def dashboard(
    today: bool = typer.Option(False, "--today", help="Filter dashboard metrics for today"),
    week: bool = typer.Option(False, "--week", help="Filter dashboard metrics for past 7 days"),
    month: bool = typer.Option(False, "--month", help="Filter dashboard metrics for past 30 days"),
    session_id: Optional[str] = typer.Option(None, "--session", help="Filter dashboard metrics for a specific session ID"),
    json_out: bool = typer.Option(False, "--json", help="Output raw JSON dashboard"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output raw Markdown dashboard"),
    export: Optional[str] = typer.Option(None, "--export", help="Export dashboard report to file (.md, .json)")
):
    """Display interactive development analytics dashboard."""
    storage = get_storage()
    engine = DashboardEngine(storage)

    metrics = engine.compute_metrics(today=today, week=week, month=month, session_id=session_id)

    if export:
        file_path = DashboardExporter.export(metrics, export)
        console.print(f"[green]Exported analytics dashboard to {file_path}[/green]")
        return

    if json_out:
        console.print(DashboardFormatter.to_json(metrics))
        return

    if markdown_out:
        console.print(DashboardFormatter.to_markdown(metrics))
        return

    renderer = DashboardRenderer(console)
    renderer.render(metrics)

def search(
    query: str = typer.Argument(..., help="Search query keyword or pattern"),
    event_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by event type / category (filesystem, git, ai, session)"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Filter by session ID"),
    today: bool = typer.Option(False, "--today", help="Filter events for today"),
    week: bool = typer.Option(False, "--week", help="Filter events for past 7 days"),
    since: Optional[str] = typer.Option(None, "--since", help="Filter events since date (YYYY-MM-DD)"),
    until: Optional[str] = typer.Option(None, "--until", help="Filter events until date (YYYY-MM-DD)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit max search results"),
    json_out: bool = typer.Option(False, "--json", help="Output search results as JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output search results as Markdown"),
    export: Optional[str] = typer.Option(None, "--export", help="Export search results to file (.md, .json)")
):
    """Instantly search all recorded project events stored in SQLite."""
    try:
        storage = get_storage()
        engine = SearchEngine(storage)
        results = engine.search_events(
            query=query,
            category=event_type,
            session=session_id,
            since=since,
            until=until,
            today=today,
            week=week,
            limit=limit,
            export=export
        )

        if export:
            file_path = SearchExporter.export(results, export)
            console.print(f"[green]Exported search results to {file_path}[/green]")
            return

        if json_out:
            console.print(SearchFormatter.to_json(results))
            return

        if markdown_out:
            console.print(SearchFormatter.to_markdown(results))
            return

        renderer = SearchRenderer(console)
        renderer.render(results)
    except Exception as e:
        console.print(f"[red]Search Error:[/red] {str(e)}")

def doctor():
    """Run diagnostics."""
    console.print("[blue]Running Prometra diagnostics...[/blue]")
    import sys
    console.print(f"Python version: {sys.version.split(' ')[0]} - [green]OK[/green]")
    
    db_path = os.path.abspath(os.path.join(".prometra", "prometra.db"))
    if os.path.exists(db_path):
        console.print(f"SQLite database: {db_path} - [green]OK[/green]")
    else:
        console.print(f"SQLite database: {db_path} - [red]MISSING[/red]")
        
    if os.path.exists(".git"):
        console.print("Git repository: [green]OK[/green]")
    else:
        console.print("Git repository: [yellow]MISSING[/yellow]")
        
    console.print("[green]Diagnostics complete.[/green]")

def config():
    """Show the effective configuration."""
    from prometra.core.config import PrometraConfig
    cfg = PrometraConfig()
    console.print("[blue]Prometra Configuration:[/blue]")
    for k, v in cfg.model_dump().items():
        console.print(f"{k}: {v}")

def version():
    """Display Prometra version."""
    console.print("Prometra Version: 2.3.0")
    console.print("Schema Version: 1.0")

def export():
    """Export project tracking data to ZIP archive."""
    import zipfile
    project_id = os.path.basename(os.path.abspath("."))
    report() # Ensure reports are generated
    
    export_dir = ".prometra/export"
    os.makedirs(export_dir, exist_ok=True)
    
    zip_path = os.path.join(export_dir, f"prometra_export_{project_id}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        reports_path = ".prometra/reports"
        if os.path.exists(reports_path):
            for root, _, files in os.walk(reports_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.join("reports", file))
                    
        db_path = ".prometra/prometra.db"
        if os.path.exists(db_path):
            zipf.write(db_path, "prometra.db")
            
    console.print(f"[green]Exported to {zip_path}[/green]")

def diff(
    file_path: str = typer.Argument(..., help="Path to the file to diff"),
    session: Optional[str] = typer.Option(None, "--session", help="Filter by session ID"),
    from_event: Optional[int] = typer.Option(None, "--from-event", help="Start event ID"),
    to_event: Optional[int] = typer.Option(None, "--to-event", help="End event ID"),
    latest: bool = typer.Option(False, "--latest", help="Diff the latest two versions"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output as Markdown"),
    context: int = typer.Option(3, "--context", help="Number of context lines for diff"),
):
    """Inspect changes between tracked file versions."""
    storage = get_storage()
    from prometra.diff.engine import DiffEngine
    from prometra.diff.renderer import DiffRenderer
    from prometra.diff.formatter import DiffFormatter

    engine = DiffEngine(storage)
    try:
        result = engine.compute_diff(
            file_path=file_path,
            session_id=session,
            from_event=from_event,
            to_event=to_event,
            latest=latest,
            context=context
        )
        if json_out:
            console.print(DiffFormatter.to_json(result))
            return
        if markdown_out:
            console.print(DiffFormatter.to_markdown(result))
            return

        renderer = DiffRenderer(console)
        renderer.render(result)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

def compare(
    session_a: Optional[str] = typer.Argument(None, help="First session ID to compare"),
    session_b: Optional[str] = typer.Argument(None, help="Second session ID to compare"),
    latest: bool = typer.Option(False, "--latest", help="Compare the two most recent sessions"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output as Markdown"),
    export_path: Optional[str] = typer.Option(None, "--export", help="Path to export comparison report file"),
):
    """Compare metrics and activity between two development sessions."""
    storage = get_storage()
    from prometra.compare.engine import CompareEngine
    from prometra.compare.renderer import CompareRenderer
    from prometra.compare.formatter import CompareFormatter
    from prometra.compare.exporter import CompareExporter

    engine = CompareEngine(storage)
    try:
        result = engine.compare_sessions(
            session_a=session_a,
            session_b=session_b,
            latest=latest
        )

        if export_path:
            format_override = "json" if json_out else ("markdown" if markdown_out else None)
            CompareExporter.export_to_file(result, export_path, format_override=format_override)
            console.print(f"[green]Exported comparison report to {export_path}[/green]")
            return

        if json_out:
            console.print(CompareFormatter.to_json(result))
            return

        if markdown_out:
            console.print(CompareFormatter.to_markdown(result))
            return

        renderer = CompareRenderer(console)
        renderer.render(result)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

def ui():
    """Launch the interactive terminal user interface (TUI)."""
    try:
        from prometra.tui.app import PrometraTUI
        storage = get_storage()
        tui = PrometraTUI(storage=storage)
        tui.run()
    except Exception as e:
        console.print(f"[red]Error launching Prometra TUI:[/red] {str(e)}")

def insights(
    session: Optional[str] = typer.Option(None, "--session", help="Session ID to analyze"),
    today: bool = typer.Option(False, "--today", help="Analyze today's session"),
    latest: bool = typer.Option(False, "--latest", help="Analyze the latest recorded session"),
    json_out: bool = typer.Option(False, "--json", help="Output insights as JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output insights as Markdown"),
    csv_out: bool = typer.Option(False, "--csv", help="Output insights as CSV"),
):
    """Analyze development sessions and generate AI session intelligence & recommendations."""
    storage = get_storage()
    from prometra.intelligence.analyzer import IntelligenceAnalyzer

    analyzer = IntelligenceAnalyzer(storage)
    try:
        result = analyzer.analyze_session(session_id=session)

        if json_out:
            console.print(analyzer.to_json(result))
            return

        if markdown_out:
            console.print(analyzer.to_markdown(result))
            return

        if csv_out:
            console.print(analyzer.to_csv(result))
            return

        # Default Rich Panel Display
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        s = result.summary
        c = result.classification
        p = result.productivity
        ai = result.ai_usage

        summary_table = Table("Metric", "Value", expand=True)
        summary_table.add_row("Session ID", s.session_id)
        summary_table.add_row("Classification", f"[bold cyan]{c.primary_category}[/bold cyan] (Confidence: {c.confidence:.0%})")
        summary_table.add_row("Productivity Score", f"[bold green]{p.score} / 100[/bold green] ({p.stars})")
        summary_table.add_row("Duration", f"{s.duration_minutes:.1f} mins ({s.duration_hours:.2f} hrs)")
        summary_table.add_row("Files Modified / Created / Deleted", f"{s.files_modified} / {s.files_created} / {s.files_deleted}")
        summary_table.add_row("Git Commits", str(s.git_commits))
        summary_table.add_row("AI Prompts Used", str(ai.total_prompts))
        summary_table.add_row("Estimated AI Cost", f"${ai.estimated_cost:.3f}")
        summary_table.add_row("Languages", ", ".join(s.languages))

        console.print(Panel(summary_table, title="🚀 Prometra AI Session Intelligence", border_style="cyan"))

        if result.patterns:
            pat_text = Text()
            for pat in result.patterns:
                pat_text.append(f"• [{pat.name}] ({pat.severity}): {pat.description}\n", style="yellow")
            console.print(Panel(pat_text, title="🔍 Detected Coding Patterns", border_style="yellow"))

        if result.recommendations:
            rec_text = Text()
            for rec in result.recommendations:
                rec_text.append(f"• {rec.title} ({rec.priority.upper()}):\n", style="bold cyan")
                rec_text.append(f"  {rec.action_item}\n\n", style="dim white")
            console.print(Panel(rec_text, title="💡 Actionable Developer Recommendations", border_style="green"))

    except Exception as e:
        console.print(f"[red]Error analyzing session insights:[/red] {str(e)}")

def checkpoint(
    message: str = typer.Argument("Checkpoint", help="Message summary for checkpoint"),
    session: Optional[str] = typer.Option(None, "--session", help="Session ID associated with checkpoint")
):
    """Create a new local development state checkpoint."""
    storage = get_storage()
    from prometra.timemachine.checkpoint import CheckpointManager

    mgr = CheckpointManager(storage)
    try:
        cp = mgr.create_checkpoint(message=message, session_id=session)
        console.print(f"[bold green]✓ Created Checkpoint:[/bold green] [cyan]{cp.id}[/cyan]")
        console.print(f"Message: {cp.message}")
        console.print(f"Branch: {cp.git_branch} ({cp.git_commit}) | Files Tracked: {len(cp.modified_files)}")
    except Exception as e:
        console.print(f"[red]Error creating checkpoint:[/red] {str(e)}")

def checkpoints(
    json_out: bool = typer.Option(False, "--json", help="Output checkpoints as JSON"),
    markdown_out: bool = typer.Option(False, "--markdown", help="Output checkpoints as Markdown"),
    csv_out: bool = typer.Option(False, "--csv", help="Output checkpoints as CSV")
):
    """List all saved local checkpoints."""
    storage = get_storage()
    from prometra.timemachine.checkpoint import CheckpointManager
    from rich.table import Table
    from rich.panel import Panel

    mgr = CheckpointManager(storage)
    cps = mgr.list_checkpoints()

    if json_out:
        import json
        data = [c.model_dump(mode="json") for c in cps]
        console.print(json.dumps(data, indent=2))
        return

    if markdown_out:
        lines = ["# Prometra Checkpoints", ""]
        for c in cps:
            lines.append(f"## {c.id} ({c.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            lines.append(f"- **Message:** {c.message}")
            lines.append(f"- **Branch:** {c.git_branch} (`{c.git_commit}`)")
            lines.append(f"- **Productivity Score:** {c.productivity_score}/100")
            lines.append(f"- **Files Modified:** {len(c.modified_files)}\n")
        console.print("\n".join(lines))
        return

    if csv_out:
        import csv, io
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["ID", "Timestamp", "Message", "Branch", "Commit", "FilesCount", "Score"])
        for c in cps:
            w.writerow([c.id, c.timestamp.strftime("%Y-%m-%d %H:%M:%S"), c.message, c.git_branch, c.git_commit, len(c.modified_files), c.productivity_score])
        console.print(out.getvalue())
        return

    tbl = Table("Checkpoint ID", "Timestamp", "Branch", "Commit", "Files", "Score", "Message", expand=True)
    for c in cps:
        t_str = c.timestamp.strftime("%Y-%m-%d %H:%M:%S") if c.timestamp else "N/A"
        tbl.add_row(f"[cyan]{c.id}[/cyan]", t_str, c.git_branch, c.git_commit, str(len(c.modified_files)), f"{c.productivity_score}/100", c.message)

    console.print(Panel(tbl, title="📍 Prometra Time Machine Checkpoints", border_style="cyan"))

def restore(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to restore"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip interactive confirmation prompt")
):
    """Restore project state to a target checkpoint."""
    from prometra.timemachine.restore import RestoreEngine
    from rich.table import Table
    from rich.panel import Panel

    engine = RestoreEngine()
    try:
        preview = engine.preview_restore(checkpoint_id)

        console.print(f"[bold yellow]🔍 PREVIEW RESTORE FOR CHECKPOINT:[/bold yellow] [cyan]{checkpoint_id}[/cyan]\n")

        tbl = Table("Change Type", "File Path", expand=True)
        for f in preview.files_created:
            tbl.add_row("[green]CREATED (To Add)[/green]", f)
        for f in preview.files_modified:
            tbl.add_row("[yellow]MODIFIED (To Overwrite)[/yellow]", f)
        for f in preview.files_deleted:
            tbl.add_row("[red]DELETED (To Remove)[/red]", f)

        console.print(Panel(tbl, title="Affected Files Summary", border_style="yellow"))
        console.print(f"Total Affected: [green]{len(preview.files_created)} created[/green], [yellow]{len(preview.files_modified)} modified[/yellow], [red]{len(preview.files_deleted)} deleted[/red]\n")

        if not confirm:
            do_restore = typer.confirm("⚠️ Are you sure you want to restore workspace files to this checkpoint?")
            if not do_restore:
                console.print("[yellow]Restore operation cancelled.[/yellow]")
                return

        engine.execute_restore(checkpoint_id)
        console.print(f"[bold green]✓ Successfully restored workspace to checkpoint '{checkpoint_id}'![/bold green]")

    except Exception as e:
        console.print(f"[red]Error restoring checkpoint:[/red] {str(e)}")

def compare_checkpoints(
    checkpoint_a: str = typer.Argument(..., help="First checkpoint ID (A)"),
    checkpoint_b: str = typer.Argument(..., help="Second checkpoint ID (B)")
):
    """Compare differences between any two checkpoints."""
    from prometra.timemachine.compare import CheckpointComparer
    from rich.syntax import Syntax

    comparer = CheckpointComparer()
    try:
        diff = comparer.compare_checkpoints(checkpoint_a, checkpoint_b)

        console.print(f"[bold cyan]🔍 CHECKPOINT COMPARISON:[/bold cyan] [yellow]{checkpoint_a}[/yellow] vs [green]{checkpoint_b}[/green]\n")
        console.print(f"Added Files: [green]{len(diff.added_files)}[/green] | Removed Files: [red]{len(diff.removed_files)}[/red] | Modified Files: [yellow]{len(diff.modified_files)}[/yellow]\n")

        if diff.diff_text:
            syn = Syntax(diff.diff_text, "diff", theme="monokai", line_numbers=True)
            console.print(Panel(syn, title=f"Diff: {checkpoint_a} ➔ {checkpoint_b}", border_style="cyan"))
        else:
            console.print("[dim]No file differences found between checkpoints.[/dim]")

    except Exception as e:
        console.print(f"[red]Error comparing checkpoints:[/red] {str(e)}")
