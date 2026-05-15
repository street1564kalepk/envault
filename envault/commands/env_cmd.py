"""env command: spawn a subprocess with decrypted env vars injected."""

import os
import subprocess
import sys
from typing import Optional

from envault.store import load_vault, vault_exists
from envault.crypto import decrypt


def run_with_env(
    project: str,
    password: str,
    command: list[str],
    override: bool = True,
) -> int:
    """
    Decrypt the vault for *project* and run *command* with those variables
    injected into the environment.

    Args:
        project:  vault / project name.
        password: master password for decryption.
        command:  argv list to execute (e.g. ["python", "app.py"]).
        override: when True, vault values overwrite existing shell variables;
                  when False, existing shell variables take precedence.

    Returns:
        Exit-code of the child process.

    Raises:
        FileNotFoundError: vault does not exist.
        ValueError:        vault contains no variables.
        PermissionError:   wrong password / decryption failure.
    """
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    vault = load_vault(project, password)
    variables: dict = vault.get("variables", {})

    if not variables:
        raise ValueError(f"Vault '{project}' has no variables to inject.")

    env = os.environ.copy()
    injected: list[str] = []

    for key, meta in variables.items():
        try:
            value = decrypt(meta["value"], password)
        except Exception as exc:
            raise PermissionError(
                f"Failed to decrypt '{key}': {exc}"
            ) from exc

        if override or key not in env:
            env[key] = value
            injected.append(key)

    result = subprocess.run(command, env=env)
    return result.returncode
