import pytest
from typer.testing import CliRunner
import os
from prometra.cli.main import app
from prometra.storage.sqlite import SQLiteStorage

runner = CliRunner()

def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Running Prometra diagnostics" in result.stdout

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Prometra Version" in result.stdout

def test_config():
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Prometra Configuration" in result.stdout

def test_init_and_status():
    runner.invoke(app, ["init"])
    assert os.path.exists(".prometra/prometra.db")
    
    # Status should show no active session initially
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "No active session" in result.stdout
    
    # Start and stop require mocking or background processing, so we just test history and timeline
    res_hist = runner.invoke(app, ["history", "--json"])
    assert res_hist.exit_code == 0
    
    res_tl = runner.invoke(app, ["timeline"])
    assert res_tl.exit_code == 0
