"""Tests for the vault password rotation feature."""

import os
import pytest
from click.testing import CliRunner
from envault.cli import cli
from envault.commands.rotate_cmd import rotate_password
from envault.store import load_vault, vault_exists


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    """Redirect vault storage to a temporary directory."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def initialized_vault(isolated_vault_dir, runner):
    """Create and populate a vault for 'testproject'."""
    runner.invoke(cli, ["init", "testproject"], input="secret\nsecret\n")
    runner.invoke(cli, ["set", "testproject", "KEY1", "value1"], input="secret\n")
    runner.invoke(cli, ["set", "testproject", "KEY2", "value2"], input="secret\n")
    return "testproject"


def test_rotate_password_success(initialized_vault, isolated_vault_dir):
    """Rotating the password should allow loading the vault with the new password."""
    count = rotate_password("testproject", "secret", "newsecret")
    assert count == 2

    vault = load_vault("testproject", "newsecret")
    assert vault["KEY1"] == "value1"
    assert vault["KEY2"] == "value2"


def test_rotate_wrong_old_password_raises(initialized_vault, isolated_vault_dir):
    """Providing the wrong old password should raise a ClickException."""
    import click

    with pytest.raises(click.ClickException):
        rotate_password("testproject", "wrongpassword", "newsecret")


def test_rotate_nonexistent_vault_raises(isolated_vault_dir):
    """Rotating a non-existent vault should raise a ClickException."""
    import click

    with pytest.raises(click.ClickException, match="No vault found"):
        rotate_password("ghost", "old", "new")


def test_rotate_same_password_raises_via_cli(initialized_vault, runner):
    """CLI should reject rotation when old and new passwords are identical."""
    result = runner.invoke(
        cli,
        ["rotate", "testproject"],
        input="secret\nsecret\nsecret\n",
    )
    assert result.exit_code != 0
    assert "differ" in result.output


def test_rotate_cmd_cli_success(initialized_vault, runner):
    """CLI rotate command should report success and re-encrypt variables."""
    result = runner.invoke(
        cli,
        ["rotate", "testproject"],
        input="secret\nnewsecret\nnewsecret\n",
    )
    assert result.exit_code == 0
    assert "rotated successfully" in result.output
    assert "2 variable(s)" in result.output

    vault = load_vault("testproject", "newsecret")
    assert vault["KEY1"] == "value1"
