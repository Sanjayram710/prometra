import typer
import os
import time
from rich.console import Console
from prometra.storage.sqlite import SQLiteStorage
from prometra.tracker.session import SessionManager
from prometra.timeline.engine import TimelineEngine
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
