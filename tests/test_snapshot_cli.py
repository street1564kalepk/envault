"""CLI-level tests for the snapshot command group."""

import pytest
from click.testing import CliRunner

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.snapshot_cli import snapshot_group

PROJECT = "cli_snap"
PASSWORD = "cli_pass"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def prepped_vault(isolated_vault_dir):
    init_vault(PROJECT, PASSWORD)
    set_var(PROJECT, PASSWORD, "KEY1", "val1")
    return isolated_vault_dir


def _invoke(runner, *args):
    return runner.invoke(snapshot_group, list(args), catch_exceptions=False)


def test_snapshot_create_cli(runner, prepped_vault):
    result = _invoke(runner, "create", "v1", "-p", PROJECT, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "v1" in result.output
    assert "created" in result.output


def test_snapshot_list_cli(runner, prepped_vault):
    _invoke(runner, "create", "v1", "-p", PROJECT, "--password", PASSWORD)
    result = _invoke(runner, "list", "-p", PROJECT, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "v1" in result.output
    assert "1 vars" in result.output


def test_snapshot_list_empty_cli(runner, prepped_vault):
    result = _invoke(runner, "list", "-p", PROJECT, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_snapshot_restore_cli(runner, prepped_vault):
    _invoke(runner, "create", "v1", "-p", PROJECT, "--password", PASSWORD)
    result = _invoke(runner, "restore", "v1", "-p", PROJECT, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_snapshot_delete_cli(runner, prepped_vault):
    _invoke(runner, "create", "v1", "-p", PROJECT, "--password", PASSWORD)
    result = _invoke(runner, "delete", "v1", "-p", PROJECT, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_snapshot_create_duplicate_cli_error(runner, prepped_vault):
    _invoke(runner, "create", "v1", "-p", PROJECT, "--password", PASSWORD)
    result = runner.invoke(
        snapshot_group,
        ["create", "v1", "-p", PROJECT, "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_snapshot_restore_missing_cli_error(runner, prepped_vault):
    result = runner.invoke(
        snapshot_group,
        ["restore", "ghost", "-p", PROJECT, "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
    assert "not found" in result.output
