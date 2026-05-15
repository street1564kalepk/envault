"""Tests for the diff command."""
from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.diff_cmd import diff_vaults, diff_cmd


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def two_vaults(isolated_vault_dir):
    """Create two vaults with some overlapping and some unique keys."""
    init_vault("alpha", "passA")
    set_var("alpha", "passA", "SHARED", "same_value")
    set_var("alpha", "passA", "ONLY_A", "value_a")
    set_var("alpha", "passA", "DIFFER", "old_val")

    init_vault("beta", "passB")
    set_var("beta", "passB", "SHARED", "same_value")
    set_var("beta", "passB", "ONLY_B", "value_b")
    set_var("beta", "passB", "DIFFER", "new_val")
    return "alpha", "beta"


def test_diff_only_in_a(two_vaults):
    result = diff_vaults("alpha", "passA", "beta", "passB")
    assert "ONLY_A" in result["only_in_a"]
    assert "ONLY_B" not in result["only_in_a"]


def test_diff_only_in_b(two_vaults):
    result = diff_vaults("alpha", "passA", "beta", "passB")
    assert "ONLY_B" in result["only_in_b"]
    assert "ONLY_A" not in result["only_in_b"]


def test_diff_different_values(two_vaults):
    result = diff_vaults("alpha", "passA", "beta", "passB")
    assert "DIFFER" in result["different"]


def test_diff_same_values(two_vaults):
    result = diff_vaults("alpha", "passA", "beta", "passB")
    assert "SHARED" in result["same"]


def test_diff_show_values_includes_data(two_vaults):
    result = diff_vaults("alpha", "passA", "beta", "passB", show_values=True)
    assert result["values_a"]["DIFFER"] == "old_val"
    assert result["values_b"]["DIFFER"] == "new_val"


def test_diff_identical_vaults(isolated_vault_dir):
    init_vault("x", "pw")
    set_var("x", "pw", "KEY", "val")
    init_vault("y", "pw2")
    set_var("y", "pw2", "KEY", "val")
    result = diff_vaults("x", "pw", "y", "pw2")
    assert result["only_in_a"] == []
    assert result["only_in_b"] == []
    assert result["different"] == []
    assert "KEY" in result["same"]


def test_diff_missing_vault_raises(isolated_vault_dir):
    init_vault("exists", "pw")
    with pytest.raises(FileNotFoundError):
        diff_vaults("exists", "pw", "ghost", "pw")


def test_diff_cmd_output(two_vaults, runner, isolated_vault_dir):
    result = runner.invoke(
        diff_cmd,
        ["alpha", "beta",
         "--password-a", "passA",
         "--password-b", "passB"],
    )
    assert result.exit_code == 0
    assert "ONLY_A" in result.output
    assert "ONLY_B" in result.output
    assert "DIFFER" in result.output


def test_diff_cmd_show_values(two_vaults, runner, isolated_vault_dir):
    result = runner.invoke(
        diff_cmd,
        ["alpha", "beta",
         "--password-a", "passA",
         "--password-b", "passB",
         "--show-values"],
    )
    assert result.exit_code == 0
    assert "old_val" in result.output
    assert "new_val" in result.output


def test_diff_cmd_identical_message(runner, isolated_vault_dir):
    init_vault("p", "pw")
    init_vault("q", "pw2")
    result = runner.invoke(
        diff_cmd,
        ["p", "q", "--password-a", "pw", "--password-b", "pw2"],
    )
    assert result.exit_code == 0
    assert "identical" in result.output
