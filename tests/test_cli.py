import os

from typer.testing import CliRunner

from prometra.cli.main import app

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
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            runner.invoke(app, ["init"])
            assert os.path.exists(".prometra/prometra.db")

            # Status should show no active session initially
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0
            assert "No active session" in result.stdout

            # Test history and timeline
            res_hist = runner.invoke(app, ["history", "--json"])
            assert res_hist.exit_code == 0

            res_tl = runner.invoke(app, ["timeline"])
            assert res_tl.exit_code == 0
        finally:
            os.chdir(old_cwd)
