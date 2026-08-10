import json
import os

import typer
from rich.console import Console
from rich.table import Table

from prometra.connectors.models import ConnectorConfig
from prometra.connectors.registry import ConnectorRegistry

app = typer.Typer(help="Manage Prometra AI and Sync Connectors")
console = Console()


def get_connectors_config_path():
    return os.path.abspath(os.path.join(".prometra", "connectors.json"))


def load_config():
    path = get_connectors_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}


def save_config(config):
    path = get_connectors_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def get_registry():
    registry = ConnectorRegistry()
    registry.discover_plugins()
    return registry


@app.command("list")
def list_connectors():
    """List all discovered connectors."""
    registry = get_registry()
    cfg = load_config()

    table = Table("Name", "Version", "Status", "Enabled")

    connectors = registry.list()
    if not connectors:
        console.print("[yellow]No connectors discovered.[/yellow]")
        return

    for name in connectors:
        connector_cls = registry.get(name)
        connector = connector_cls()
        meta = connector.metadata()
        enabled = cfg.get(name, {}).get("enabled", True)

        status = "unknown"
        if enabled:
            try:
                connector.initialize(ConnectorConfig())
                health = connector.health()
                status = health.state
            except Exception:  # noqa: BLE001
                status = "error"
        else:
            status = "disabled"

        table.add_row(meta.name, meta.version, status, "Yes" if enabled else "No")

    console.print(table)


@app.command("info")
def info(connector: str = typer.Argument(..., help="Name of the connector")):
    """Show detailed information about a connector."""
    registry = get_registry()
    try:
        connector_cls = registry.get(connector)
    except KeyError:
        console.print(f"[red]Connector '{connector}' not found.[/red]")
        raise typer.Exit(1)

    instance = connector_cls()
    meta = instance.metadata()
    cfg = load_config()
    enabled = cfg.get(connector, {}).get("enabled", True)

    console.print(f"[blue]Connector:[/blue] {meta.name} (v{meta.version})")
    console.print(f"[blue]Enabled:[/blue] {'Yes' if enabled else 'No'}")
    console.print(
        f"[blue]Supported Models:[/blue] {', '.join(meta.supported_models) or 'None'}"
    )
    console.print(
        f"[blue]Supported Events:[/blue] {', '.join(meta.supported_events) or 'None'}"
    )

    if enabled:
        try:
            instance.initialize(ConnectorConfig())
            health = instance.health()
            console.print(f"[blue]Health Status:[/blue] {health.state}")
            if health.error_message:
                console.print(f"[red]Error:[/red] {health.error_message}")
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]Initialization Error:[/red] {e}")


@app.command("enable")
def enable(connector: str = typer.Argument(..., help="Name of the connector")):
    """Enable a connector."""
    registry = get_registry()
    if connector not in registry.list():
        console.print(f"[red]Connector '{connector}' not found.[/red]")
        raise typer.Exit(1)

    cfg = load_config()
    if connector not in cfg:
        cfg[connector] = {}
    cfg[connector]["enabled"] = True
    save_config(cfg)
    console.print(f"[green]Connector '{connector}' enabled.[/green]")


@app.command("disable")
def disable(connector: str = typer.Argument(..., help="Name of the connector")):
    """Disable a connector."""
    registry = get_registry()
    if connector not in registry.list():
        console.print(f"[red]Connector '{connector}' not found.[/red]")
        raise typer.Exit(1)

    cfg = load_config()
    if connector not in cfg:
        cfg[connector] = {}
    cfg[connector]["enabled"] = False
    save_config(cfg)
    console.print(f"[yellow]Connector '{connector}' disabled.[/yellow]")


@app.command("health")
def health():
    """Run health checks for all enabled connectors."""
    registry = get_registry()
    cfg = load_config()

    table = Table("Connector", "Status", "Error")

    for name in registry.list():
        enabled = cfg.get(name, {}).get("enabled", True)
        if not enabled:
            continue

        cls = registry.get(name)
        instance = cls()
        try:
            instance.initialize(ConnectorConfig())
            status = instance.health()
            table.add_row(name, status.state, status.error_message or "-")
        except Exception as e:  # noqa: BLE001
            table.add_row(name, "error", str(e))

    if table.row_count == 0:
        console.print("[yellow]No enabled connectors to check.[/yellow]")
    else:
        console.print(table)


@app.command("validate")
def validate():
    """Validate connector registration."""
    console.print("[blue]Validating Connectors...[/blue]")
    registry = ConnectorRegistry()
    from importlib.metadata import entry_points

    try:
        eps = entry_points(group="prometra.connectors")
    except Exception:  # noqa: BLE001
        eps = []

    issues = 0
    names_seen = set()
    for ep in eps:
        name = ep.name
        if name in names_seen:
            console.print(f"[red]Error:[/red] Duplicate connector name '{name}' found.")
            issues += 1
        names_seen.add(name)
        try:
            cls = ep.load()
            registry.validate(cls)
            instance = cls()
            meta = instance.metadata()
            if not meta.name or not meta.version:
                console.print(
                    f"[red]Error:[/red] Connector '{name}' is missing metadata fields."
                )
                issues += 1
        except Exception as e:  # noqa: BLE001
            console.print(
                f"[red]Error:[/red] Connector '{name}' failed validation: {e}"
            )
            issues += 1

    if issues == 0:
        console.print("[green]All discovered connectors passed validation.[/green]")
    else:
        console.print(f"[red]Validation finished with {issues} issues.[/red]")
        raise typer.Exit(1)


@app.command("serve")
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on."),
    host: str = typer.Option("localhost", "--host", "-h", help="Host address."),
):
    """Start live local Prometra MCP HTTP JSON-RPC Server."""
    from demo.mcp_server import HTTPServer, MCPRequestHandler
    console.print(f"[bold green]🚀 Starting Prometra MCP Server on http://{host}:{port}/mcp[/bold green]")
    server = HTTPServer((host, port), MCPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("[yellow]Stopping MCP Server...[/yellow]")
        server.server_close()

