"""Unit tests for envault.commands.env_cmd.run_with_env."""

import os
import pytest

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.env_cmd import run_with_env


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def initialized_vault(isolated_vault_dir):
    init_vault("testproject", "secret")
    set_var("testproject", "secret", "HELLO", "world")
    set_var("testproject", "secret", "NUM", "42")
    return "testproject"


def test_run_injects_variables(initialized_vault):
    """Child process should see decrypted env vars."""
    code = run_with_env(
        project=initialized_vault,
        password="secret",
        command=["python", "-c", "import os, sys; sys.exit(0 if os.environ.get('HELLO')=='world' else 1)"],
    )
    assert code == 0


def test_run_no_override_keeps_existing(initialized_vault, monkeypatch):
    """With override=False, pre-existing shell variable must not be replaced."""
    monkeypatch.setenv("HELLO", "original")
    code = run_with_env(
        project=initialized_vault,
        password="secret",
        command=["python", "-c", "import os, sys; sys.exit(0 if os.environ['HELLO']=='original' else 1)"],
        override=False,
    )
    assert code == 0


def test_run_override_replaces_existing(initialized_vault, monkeypatch):
    """With override=True (default), vault value replaces existing shell variable."""
    monkeypatch.setenv("HELLO", "original")
    code = run_with_env(
        project=initialized_vault,
        password="secret",
        command=["python", "-c", "import os, sys; sys.exit(0 if os.environ['HELLO']=='world' else 1)"],
        override=True,
    )
    assert code == 0


def test_run_nonexistent_vault_raises(isolated_vault_dir):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        run_with_env("ghost", "pw", ["echo", "hi"])


def test_run_wrong_password_raises(initialized_vault):
    with pytest.raises(PermissionError):
        run_with_env(initialized_vault, "wrongpass", ["echo", "hi"])


def test_run_empty_vault_raises(isolated_vault_dir):
    init_vault("empty", "secret")
    with pytest.raises(ValueError, match="no variables"):
        run_with_env("empty", "secret", ["echo", "hi"])


def test_child_exit_code_propagated(initialized_vault):
    """The exit code of the child process is returned as-is."""
    code = run_with_env(
        project=initialized_vault,
        password="secret",
        command=["python", "-c", "import sys; sys.exit(7)"],
    )
    assert code == 7
