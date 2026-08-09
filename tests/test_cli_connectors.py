
from typer.testing import CliRunner

from prometra.cli.main import app

runner = CliRunner()


def test_connectors_list():
    result = runner.invoke(app, ["connectors", "list"])
    assert result.exit_code == 0
    # Output will likely say 'No connectors discovered' since none are installed via pip
    # but the command should run successfully without exceptions.


def test_connectors_health():
    result = runner.invoke(app, ["connectors", "health"])
    assert result.exit_code == 0
    # Expected: "No enabled connectors to check." or table


def test_connectors_validate():
    result = runner.invoke(app, ["connectors", "validate"])
    assert result.exit_code == 0
    assert "Validating Connectors" in result.stdout


def test_connectors_enable_disable_not_found():
    result = runner.invoke(app, ["connectors", "enable", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.stdout

    result = runner.invoke(app, ["connectors", "disable", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_connectors_info_not_found():
    result = runner.invoke(app, ["connectors", "info", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.stdout
