import typer
from rich.console import Console
from rich.table import Table
from prometra.plugins.manager import PluginManager
from prometra.plugins.exceptions import PluginNotFoundError

app = typer.Typer(help="Manage Prometra plugins and extensions", invoke_without_command=True)
console = Console()

def get_manager() -> PluginManager:
    pm = PluginManager()
    pm.load_plugins()
    return pm

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """List installed plugins if no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        list_plugins()

@app.command("list")
def list_plugins():
    """List all installed plugins, version, status, and description."""
    pm = get_manager()
    summary = pm.get_status_summary()

    table = Table("Name", "Version", "Status", "Author", "Description")

    if not summary:
        console.print("[yellow]No plugins installed or discovered.[/yellow]")
        return

    for item in summary:
        status_str = f"[green]enabled[/green]" if item["status"] == "enabled" else f"[yellow]disabled[/yellow]"
        table.add_row(
            item["name"],
            item["version"],
            status_str,
            item["author"] or "N/A",
            item["description"] or ""
        )

    console.print(table)

@app.command("enable")
def enable(plugin_name: str = typer.Argument(..., help="Name of the plugin to enable")):
    """Enable a plugin by name."""
    pm = get_manager()
    try:
        pm.enable_plugin(plugin_name)
        console.print(f"[green]Enabled plugin '{plugin_name}'.[/green]")
    except PluginNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Failed to enable plugin:[/red] {e}")

@app.command("disable")
def disable(plugin_name: str = typer.Argument(..., help="Name of the plugin to disable")):
    """Disable a plugin by name."""
    pm = get_manager()
    try:
        pm.disable_plugin(plugin_name)
        console.print(f"[yellow]Disabled plugin '{plugin_name}'.[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to disable plugin:[/red] {e}")

@app.command("reload")
def reload():
    """Reload plugin discovery and configurations."""
    pm = get_manager()
    try:
        reloaded = pm.reload_plugins()
        console.print(f"[green]Reloaded plugins successfully ({len(reloaded)} active).[/green]")
    except Exception as e:
        console.print(f"[red]Failed to reload plugins:[/red] {e}")
