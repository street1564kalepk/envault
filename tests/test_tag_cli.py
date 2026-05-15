"""CLI-level tests for the tag sub-commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.tag_cli import tag_group

PROJECT = "tagclitest"
PASSWORD = "cli_pass"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    monkeypatch.setenv("ENVAULT_PROJECT", PROJECT)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def prepped_vault(isolated_vault_dir):
    init_vault(PROJECT, PASSWORD)
    set_var(PROJECT, PASSWORD, "SECRET_KEY", "topsecret")
    set_var(PROJECT, PASSWORD, "DB_URL", "postgres://localhost/db")
    return isolated_vault_dir


def _invoke(runner, args, password=PASSWORD):
    return runner.invoke(tag_group, args + ["--password", password])


def test_tag_add_cli(runner, prepped_vault):
    result = _invoke(runner, ["add", "SECRET_KEY", "sensitive"])
    assert result.exit_code == 0
    assert "added" in result.output


def test_tag_add_duplicate_cli(runner, prepped_vault):
    _invoke(runner, ["add", "SECRET_KEY", "sensitive"])
    result = _invoke(runner, ["add", "SECRET_KEY", "sensitive"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_tag_remove_cli(runner, prepped_vault):
    _invoke(runner, ["add", "DB_URL", "database"])
    result = _invoke(runner, ["remove", "DB_URL", "database"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_tag_list_all_cli(runner, prepped_vault):
    _invoke(runner, ["add", "SECRET_KEY", "sensitive"])
    _invoke(runner, ["add", "DB_URL", "database"])
    result = _invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "sensitive" in result.output
    assert "database" in result.output


def test_tag_list_for_key_cli(runner, prepped_vault):
    _invoke(runner, ["add", "SECRET_KEY", "sensitive"])
    result = _invoke(runner, ["list", "--key", "SECRET_KEY"])
    assert result.exit_code == 0
    assert "sensitive" in result.output


def test_tag_filter_cli(runner, prepped_vault):
    _invoke(runner, ["add", "SECRET_KEY", "sensitive"])
    result = _invoke(runner, ["filter", "sensitive"])
    assert result.exit_code == 0
    assert "SECRET_KEY" in result.output


def test_tag_filter_no_match_cli(runner, prepped_vault):
    result = _invoke(runner, ["filter", "nonexistent"])
    assert result.exit_code == 0
    assert "No variables" in result.output
