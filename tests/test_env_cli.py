"""CLI integration tests for `envault env`."""

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def prepped_vault(isolated_vault_dir):
    init_vault("myapp", "secret")
    set_var("myapp", "secret", "APP_ENV", "production")
    return "myapp"


def _invoke(runner, args, password="secret"):
    return runner.invoke(cli, args, input=password + "\n", catch_exceptions=False)


def test_env_runs_command(runner, prepped_vault):
    result = _invoke(
        runner,
        ["env", "--project", "myapp", "--", "python", "-c",
         "import os, sys; sys.exit(0 if os.environ.get('APP_ENV')=='production' else 1)"],
    )
    assert result.exit_code == 0


def test_env_missing_project_errors(runner, isolated_vault_dir, monkeypatch):
    monkeypatch.delenv("ENVAULT_PROJECT", raising=False)
    result = runner.invoke(
        cli,
        ["env", "--password", "secret", "--", "echo", "hi"],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
    assert "No project" in result.output or "Error" in result.output


def test_env_nonexistent_vault_errors(runner, isolated_vault_dir):
    result = _invoke(
        runner,
        ["env", "--project", "ghost", "--", "echo", "hi"],
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_env_no_override_flag(runner, prepped_vault, monkeypatch):
    """--no-override flag is accepted without error."""
    result = _invoke(
        runner,
        ["env", "--project", "myapp", "--no-override", "--",
         "python", "-c", "import sys; sys.exit(0)"],
    )
    assert result.exit_code == 0
