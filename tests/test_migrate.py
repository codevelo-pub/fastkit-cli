"""Tests for fastkit_cli.commands.migrate"""
from unittest.mock import patch
from typer.testing import CliRunner
from fastkit_cli.commands.migrate import app

runner = CliRunner()


class TestMigrateRun:
    def test_run_exits_successfully(self):
        with patch("fastkit_cli.commands.migrate.subprocess.run"):
            result = runner.invoke(app, ["run"])

        assert result.exit_code == 0

    def test_run_output(self):
        with patch("fastkit_cli.commands.migrate.subprocess.run"):
            result = runner.invoke(app, ["run"])

        assert "migrations" in result.output.lower()

    def test_run_calls_alembic_upgrade_head(self):
        with patch("fastkit_cli.commands.migrate.subprocess.run") as mock_run:
            runner.invoke(app, ["run"])

        cmd = mock_run.call_args.args[0]
        assert "alembic" in " ".join(cmd)
        assert "upgrade" in cmd
        assert "head" in cmd

    def test_run_alembic_not_found_exits_with_error(self):
        with patch("fastkit_cli.commands.migrate.subprocess.run", side_effect=FileNotFoundError):
            result = runner.invoke(app, ["run"])

        assert result.exit_code == 1
        assert "alembic not found" in result.output

    def test_run_alembic_error_exits_with_code(self):
        import subprocess
        with patch("fastkit_cli.commands.migrate.subprocess.run",
                   side_effect=subprocess.CalledProcessError(1, "alembic")):
            result = runner.invoke(app, ["run"])

        assert result.exit_code == 1
