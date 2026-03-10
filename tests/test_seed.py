"""Tests for fastkit_cli.commands.seed"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from fastkit_cli.commands.seed import app, _discover_seeders, _run_seeder

runner = CliRunner()


# ─────────────────────────────────────────────────────────────────────────────
# _discover_seeders
# ─────────────────────────────────────────────────────────────────────────────

class TestDiscoverSeeders:
    def test_returns_empty_list_when_no_seeders_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert _discover_seeders() == []

    def test_discovers_seeder_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seeders_dir = tmp_path / "seeders"
        seeders_dir.mkdir()
        (seeders_dir / "UserSeeder.py").write_text("")
        (seeders_dir / "InvoiceSeeder.py").write_text("")

        result = _discover_seeders()
        assert "UserSeeder" in result
        assert "InvoiceSeeder" in result

    def test_ignores_init_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seeders_dir = tmp_path / "seeders"
        seeders_dir.mkdir()
        (seeders_dir / "__init__.py").write_text("")
        (seeders_dir / "UserSeeder.py").write_text("")

        result = _discover_seeders()
        assert "__init__" not in result
        assert "UserSeeder" in result

    def test_returns_sorted_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seeders_dir = tmp_path / "seeders"
        seeders_dir.mkdir()
        (seeders_dir / "UserSeeder.py").write_text("")
        (seeders_dir / "InvoiceSeeder.py").write_text("")
        (seeders_dir / "CategorySeeder.py").write_text("")

        result = _discover_seeders()
        assert result == sorted(result)


# ─────────────────────────────────────────────────────────────────────────────
# CLI: fastkit db seed (all seeders)
# ─────────────────────────────────────────────────────────────────────────────

class TestSeedAll:
    def test_warns_when_no_seeders_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "No seeders found" in result.output

    def test_runs_all_discovered_seeders(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seeders_dir = tmp_path / "seeders"
        seeders_dir.mkdir()

        with patch("fastkit_cli.commands.seed._discover_seeders", return_value=["UserSeeder", "InvoiceSeeder"]), \
             patch("fastkit_cli.commands.seed._run_seeder") as mock_run:
            result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert mock_run.call_count == 2
        mock_run.assert_any_call("UserSeeder")
        mock_run.assert_any_call("InvoiceSeeder")

    def test_output_shows_seeder_count(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with patch("fastkit_cli.commands.seed._discover_seeders", return_value=["UserSeeder", "InvoiceSeeder"]), \
             patch("fastkit_cli.commands.seed._run_seeder"):
            result = runner.invoke(app, [])

        assert "2" in result.output


# ─────────────────────────────────────────────────────────────────────────────
# CLI: fastkit db seed UserSeeder (specific seeder)
# ─────────────────────────────────────────────────────────────────────────────

class TestSeedSpecific:
    def test_runs_specific_seeder(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with patch("fastkit_cli.commands.seed._run_seeder") as mock_run:
            result = runner.invoke(app, ["UserSeeder"])

        assert result.exit_code == 0
        mock_run.assert_called_once_with("UserSeeder")

    def test_output_shows_seeder_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with patch("fastkit_cli.commands.seed._run_seeder"):
            result = runner.invoke(app, ["UserSeeder"])

        assert "UserSeeder" in result.output


# ─────────────────────────────────────────────────────────────────────────────
# _run_seeder
# ─────────────────────────────────────────────────────────────────────────────

class TestRunSeeder:
    def test_runs_seeder_with_run_method(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seeders_dir = tmp_path / "seeders"
        seeders_dir.mkdir()
        (seeders_dir / "UserSeeder.py").write_text(
            "class UserSeeder:\n    def run(self):\n        pass\n"
        )

        # Remove cached module if exists
        sys.modules.pop("UserSeeder", None)
        _run_seeder("UserSeeder")

    def test_exits_when_seeders_dir_missing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with patch("fastkit_cli.commands.seed._load_seeder_class", side_effect=SystemExit(1)):
            result = runner.invoke(app, ["UserSeeder"])

        assert result.exit_code != 0

    def test_exits_when_run_method_missing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        seeders_dir = tmp_path / "seeders"
        seeders_dir.mkdir()
        (seeders_dir / "BadSeeder.py").write_text(
            "class BadSeeder:\n    pass\n"
        )

        sys.modules.pop("BadSeeder", None)

        with patch("fastkit_cli.commands.seed._load_seeder_class") as mock_load:
            mock_load.return_value = type("BadSeeder", (), {})  # Class without run()
            result = runner.invoke(app, ["BadSeeder"])

        assert result.exit_code == 1
        assert "run()" in result.output

    def test_exits_when_seeder_run_raises_exception(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        mock_class = MagicMock()
        mock_class.return_value.run.side_effect = Exception("DB connection failed")

        with patch("fastkit_cli.commands.seed._load_seeder_class", return_value=mock_class):
            result = runner.invoke(app, ["UserSeeder"])

        assert result.exit_code == 1
        assert "DB connection failed" in result.output
