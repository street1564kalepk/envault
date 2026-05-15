"""Tests for the rename command."""

import os
import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.rename_cmd import rename_var
from envault.store import load_vault


PASSWORD = "test-secret"
PROJECT = "rename-test-project"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def initialized_vault(isolated_vault_dir):
    init_vault(PROJECT, PASSWORD)
    set_var(PROJECT, PASSWORD, "OLD_KEY", "hello")
    set_var(PROJECT, PASSWORD, "ANOTHER", "world")
    return isolated_vault_dir


def test_rename_key_success(initialized_vault):
    rename_var(PROJECT, PASSWORD, "OLD_KEY", "NEW_KEY")
    data = load_vault(PROJECT, PASSWORD)
    assert "NEW_KEY" in data
    assert data["NEW_KEY"] == "hello"
    assert "OLD_KEY" not in data


def test_rename_preserves_other_keys(initialized_vault):
    rename_var(PROJECT, PASSWORD, "OLD_KEY", "NEW_KEY")
    data = load_vault(PROJECT, PASSWORD)
    assert "ANOTHER" in data
    assert data["ANOTHER"] == "world"


def test_rename_nonexistent_key_raises(initialized_vault):
    with pytest.raises(KeyError, match="MISSING"):
        rename_var(PROJECT, PASSWORD, "MISSING", "NEW_KEY")


def test_rename_to_existing_key_raises(initialized_vault):
    with pytest.raises(KeyError, match="ANOTHER"):
        rename_var(PROJECT, PASSWORD, "OLD_KEY", "ANOTHER")


def test_rename_no_vault_raises(isolated_vault_dir):
    with pytest.raises(FileNotFoundError, match="no-vault"):
        rename_var("no-vault", PASSWORD, "KEY", "NEW_KEY")


def test_rename_cmd_cli(runner, initialized_vault):
    result = runner.invoke(
        cli,
        ["rename", "OLD_KEY", "NEW_KEY", "--project", PROJECT, "--password", PASSWORD],
    )
    assert result.exit_code == 0, result.output
    assert "OLD_KEY" in result.output
    assert "NEW_KEY" in result.output


def test_rename_cmd_cli_missing_key(runner, initialized_vault):
    result = runner.invoke(
        cli,
        ["rename", "GHOST", "NEW_KEY", "--project", PROJECT, "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "GHOST" in result.output or "GHOST" in (result.stderr or "")


def test_rename_cmd_cli_no_vault(runner, isolated_vault_dir):
    result = runner.invoke(
        cli,
        ["rename", "KEY", "NEW_KEY", "--project", "ghost-project", "--password", PASSWORD],
    )
    assert result.exit_code != 0
