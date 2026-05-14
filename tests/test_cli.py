"""Tests for CLI commands."""

import os
import pytest
from click.testing import CliRunner
from envault.cli import cli
from envault import store


PROJECT = "test_project"
PASSWORD = "s3cr3t"


@pytest.fixture(autouse=True)
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "VAULT_DIR", str(tmp_path))
    return tmp_path


def invoke(args, input_text=None):
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(cli, args, input=input_text, catch_exceptions=False)


def test_init_creates_vault():
    result = invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code == 0
    assert "initialized successfully" in result.output


def test_init_existing_vault_abort():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    result = invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\nn\n")
    assert result.exit_code == 0
    assert "Aborted" in result.output


def test_set_and_get_variable():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    result = invoke(["set", PROJECT, "API_KEY", "abc123"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "Set 'API_KEY'" in result.output

    result = invoke(["get", PROJECT, "API_KEY"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "abc123" in result.output


def test_get_export_flag():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    invoke(["set", PROJECT, "DB_URL", "postgres://localhost"], input_text=f"{PASSWORD}\n")
    result = invoke(["get", PROJECT, "DB_URL", "--export"], input_text=f"{PASSWORD}\n")
    assert "export DB_URL=postgres://localhost" in result.output


def test_list_variables():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    invoke(["set", PROJECT, "KEY1", "val1"], input_text=f"{PASSWORD}\n")
    invoke(["set", PROJECT, "KEY2", "val2"], input_text=f"{PASSWORD}\n")
    result = invoke(["list", PROJECT], input_text=f"{PASSWORD}\n")
    assert "KEY1" in result.output
    assert "KEY2" in result.output


def test_list_show_values():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    invoke(["set", PROJECT, "TOKEN", "secret_token"], input_text=f"{PASSWORD}\n")
    result = invoke(["list", PROJECT, "--show-values"], input_text=f"{PASSWORD}\n")
    assert "TOKEN=secret_token" in result.output


def test_delete_variable():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    invoke(["set", PROJECT, "TEMP_KEY", "temp_val"], input_text=f"{PASSWORD}\n")
    result = invoke(["delete", PROJECT, "TEMP_KEY", "--yes"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "Deleted 'TEMP_KEY'" in result.output

    result = invoke(["get", PROJECT, "TEMP_KEY"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 1


def test_wrong_password_on_set():
    invoke(["init", PROJECT], input_text=f"{PASSWORD}\n{PASSWORD}\n")
    result = invoke(["set", PROJECT, "KEY", "val"], input_text="wrong_password\n")
    assert result.exit_code == 1
    assert "Invalid password" in result.output


def test_vault_not_found():
    result = invoke(["get", "nonexistent", "KEY"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 1
    assert "does not exist" in result.output
