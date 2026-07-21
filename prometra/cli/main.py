import typer
from prometra.cli import commands

app = typer.Typer(help="Prometra - The Intelligence Layer for AI-Assisted Software Development", add_completion=False)

app.command(name="init")(commands.init)
app.command(name="start")(commands.start)
app.command(name="stop")(commands.stop)
app.command(name="analyze")(commands.analyze)
app.command(name="report")(commands.report)

if __name__ == "__main__":
    app()
