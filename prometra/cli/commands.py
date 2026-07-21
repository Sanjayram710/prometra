import typer
import os
from rich.console import Console
from prometra.storage.sqlite import SQLiteStorage
from prometra.tracker.session import SessionManager
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
        console.print("[green]Initialized empty Prometra project in .prometra/[/green]")
    else:
        console.print("[yellow]Prometra project already initialized.[/yellow]")

def start():
    """Start session tracking for the current project."""
    if not os.path.exists(".prometra"):
        console.print("[red]Project not initialized. Run `prometra init` first.[/red]")
        return
        
    project_id = os.path.basename(os.path.abspath("."))
    storage = get_storage()
    sm = SessionManager(storage)
    session = sm.start_session(project_id=project_id, project_path=os.path.abspath("."), working_directory=os.path.abspath("."))
    console.print(f"[green]Started Prometra session: {session.session_id}[/green]")

def stop(session_id: str = typer.Option(None, help="Specific session ID to stop")):
    """Stop the active session gracefully."""
    storage = get_storage()
    sm = SessionManager(storage)
    if session_id:
        sm.end_session(session_id)
        console.print(f"[green]Stopped session {session_id}.[/green]")
    else:
        console.print("[yellow]Please provide --session-id to stop for now.[/yellow]")

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
    out_md = generator.generate_markdown(project_id, ".prometra/reports/report.md")
    out_json = generator.generate_json(project_id, ".prometra/reports/report.json")
    console.print(f"[green]Generated reports at {out_md} and {out_json}[/green]")
