"""Tests for envault search command."""

import os
import pytest
from click.testing import CliRunner

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.search_cmd import search_vars, search_all_vaults, search_cmd


PASSWORD = "hunter2"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def initialized_vault(isolated_vault_dir):
    init_vault("testproject", PASSWORD)
    set_var("testproject", "DATABASE_URL", "postgres://localhost/db", PASSWORD)
    set_var("testproject", "API_KEY", "secret123", PASSWORD)
    set_var("testproject", "DEBUG", "true", PASSWORD)
    return "testproject"


# --- unit-level tests ---

def test_search_by_key_match(initialized_vault):
    results = search_vars("DATABASE", PASSWORD, "testproject")
    assert len(results) == 1
    assert results[0]["key"] == "DATABASE_URL"


def test_search_case_insensitive_default(initialized_vault):
    results = search_vars("database", PASSWORD, "testproject")
    assert len(results) == 1
    assert results[0]["key"] == "DATABASE_URL"


def test_search_case_sensitive_no_match(initialized_vault):
    results = search_vars("database", PASSWORD, "testproject", case_sensitive=True)
    assert results == []


def test_search_values(initialized_vault):
    results = search_vars("secret", PASSWORD, "testproject", search_values=True)
    assert any(r["key"] == "API_KEY" for r in results)


def test_search_no_match(initialized_vault):
    results = search_vars("NONEXISTENT", PASSWORD, "testproject")
    assert results == []


def test_search_wrong_password_raises(initialized_vault):
    with pytest.raises(ValueError):
        search_vars("DATABASE", "wrongpass", "testproject")


def test_search_missing_vault_raises(isolated_vault_dir):
    with pytest.raises(FileNotFoundError):
        search_vars("KEY", PASSWORD, "ghost")


def test_search_all_vaults(isolated_vault_dir):
    init_vault("proj_a", PASSWORD)
    set_var("proj_a", "FOO", "bar", PASSWORD)
    init_vault("proj_b", PASSWORD)
    set_var("proj_b", "FOO_BAR", "baz", PASSWORD)

    results = search_all_vaults("FOO", PASSWORD)
    projects = {r["project"] for r in results}
    assert "proj_a" in projects
    assert "proj_b" in projects


# --- CLI tests ---

def test_search_cmd_found(initialized_vault, runner):
    result = runner.invoke(
        search_cmd,
        ["DATABASE", "--project", "testproject", "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_search_cmd_no_match(initialized_vault, runner):
    result = runner.invoke(
        search_cmd,
        ["NOTHING", "--project", "testproject", "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "No matches found" in result.output


def test_search_cmd_missing_vault(isolated_vault_dir, runner):
    result = runner.invoke(
        search_cmd,
        ["KEY", "--project", "ghost", "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "No vault found" in result.output
