import typer
from prometra.cli import commands

app = typer.Typer(help="Prometra - The Intelligence Layer for AI-Assisted Software Development", add_completion=False)

app.command(name="init")(commands.init)
app.command(name="start")(commands.start)
app.command(name="stop")(commands.stop)
app.command(name="analyze")(commands.analyze)
app.command(name="report")(commands.report)
app.command(name="status")(commands.status)
app.command(name="history")(commands.history)
app.command(name="timeline")(commands.timeline)
app.command(name="doctor")(commands.doctor)
app.command(name="config")(commands.config)
app.command(name="version")(commands.version)
app.command(name="export")(commands.export)

if __name__ == "__main__":
    app()
