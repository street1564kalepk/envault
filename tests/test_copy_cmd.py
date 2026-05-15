"""Tests for the copy command."""

import os
import pytest
from click.testing import CliRunner
from envault.cli import cli
from envault.store import set_vault_dir


@pytest.fixture
def isolated_vault_dir(tmp_path):
    set_vault_dir(str(tmp_path))
    yield tmp_path
    set_vault_dir(None)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def two_initialized_vaults(isolated_vault_dir, runner):
    """Create two initialized vaults: 'alpha' and 'beta'."""
    runner.invoke(cli, ["init", "alpha"], input="pass_alpha\npass_alpha\n")
    runner.invoke(cli, ["init", "beta"], input="pass_beta\npass_beta\n")
    # Set a variable in alpha
    runner.invoke(cli, ["set", "alpha", "DB_URL"], input="postgres://localhost\npass_alpha\n")
    runner.invoke(cli, ["set", "alpha", "SECRET_KEY"], input="supersecret\npass_alpha\n")
    return isolated_vault_dir


def test_copy_single_key(two_initialized_vaults, runner):
    result = runner.invoke(
        cli, ["copy", "alpha", "beta", "--key", "DB_URL"],
        input="pass_alpha\npass_beta\n"
    )
    assert result.exit_code == 0, result.output
    assert "DB_URL" in result.output
    assert "Copied 1 variable(s)" in result.output


def test_copy_all_keys(two_initialized_vaults, runner):
    result = runner.invoke(
        cli, ["copy", "alpha", "beta"],
        input="pass_alpha\npass_beta\n"
    )
    assert result.exit_code == 0, result.output
    assert "Copied 2 variable(s)" in result.output


def test_copy_verifies_value_in_destination(two_initialized_vaults, runner):
    runner.invoke(cli, ["copy", "alpha", "beta", "--key", "SECRET_KEY"],
                  input="pass_alpha\npass_beta\n")
    result = runner.invoke(cli, ["get", "beta", "SECRET_KEY"], input="pass_beta\n")
    assert result.exit_code == 0, result.output
    assert "supersecret" in result.output


def test_copy_skips_existing_without_overwrite(two_initialized_vaults, runner):
    # First copy
    runner.invoke(cli, ["copy", "alpha", "beta", "--key", "DB_URL"],
                  input="pass_alpha\npass_beta\n")
    # Second copy without overwrite
    result = runner.invoke(cli, ["copy", "alpha", "beta", "--key", "DB_URL"],
                           input="pass_alpha\npass_beta\n")
    assert result.exit_code == 0, result.output
    assert "Skipping" in result.output


def test_copy_overwrites_with_flag(two_initialized_vaults, runner):
    runner.invoke(cli, ["copy", "alpha", "beta", "--key", "DB_URL"],
                  input="pass_alpha\npass_beta\n")
    result = runner.invoke(
        cli, ["copy", "alpha", "beta", "--key", "DB_URL", "--overwrite"],
        input="pass_alpha\npass_beta\n"
    )
    assert result.exit_code == 0, result.output
    assert "Copied 1 variable(s)" in result.output


def test_copy_missing_source_vault(isolated_vault_dir, runner):
    runner.invoke(cli, ["init", "beta"], input="pass_beta\npass_beta\n")
    result = runner.invoke(cli, ["copy", "nonexistent", "beta"],
                           input="pass_alpha\npass_beta\n")
    assert result.exit_code != 0 or "does not exist" in result.output


def test_copy_missing_key_in_source(two_initialized_vaults, runner):
    result = runner.invoke(
        cli, ["copy", "alpha", "beta", "--key", "MISSING_VAR"],
        input="pass_alpha\npass_beta\n"
    )
    assert result.exit_code != 0 or "not found" in result.output
