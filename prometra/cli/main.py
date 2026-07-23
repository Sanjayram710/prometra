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
app.command(name="replay")(commands.replay)
app.command(name="dashboard")(commands.dashboard)
app.command(name="search")(commands.search)
app.command(name="doctor")(commands.doctor)
app.command(name="config")(commands.config)
app.command(name="version")(commands.version)
app.command(name="export")(commands.export)
app.command(name="diff")(commands.diff)
app.command(name="compare")(commands.compare)
app.command(name="ui")(commands.ui)

from prometra.cli.connectors_cmd import app as connectors_app
app.add_typer(connectors_app, name="connectors")

from prometra.cli.plugins_cmd import app as plugins_app
app.add_typer(plugins_app, name="plugins")

if __name__ == "__main__":
    app()
