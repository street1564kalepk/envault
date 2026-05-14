"""Persistent encrypted storage for envault project vaults."""

import json
import os
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault" / "vaults"


def _vault_path(project: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    safe_name = project.replace("/", "_").replace("\\", "_")
    return vault_dir / f"{safe_name}.vault"


def save_vault(project: str, env_vars: Dict[str, str], password: str,
               vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    """Encrypt and save env vars for a project. Returns the vault file path."""
    vault_dir.mkdir(parents=True, exist_ok=True)
    plaintext = json.dumps(env_vars)
    token = encrypt(plaintext, password)
    path = _vault_path(project, vault_dir)
    path.write_text(token, encoding="utf-8")
    return path


def load_vault(project: str, password: str,
               vault_dir: Path = DEFAULT_VAULT_DIR) -> Dict[str, str]:
    """Load and decrypt env vars for a project."""
    path = _vault_path(project, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"No vault found for project '{project}'.")
    token = path.read_text(encoding="utf-8").strip()
    plaintext = decrypt(token, password)
    return json.loads(plaintext)


def vault_exists(project: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> bool:
    """Return True if a vault file exists for the given project."""
    return _vault_path(project, vault_dir).exists()


def list_vaults(vault_dir: Path = DEFAULT_VAULT_DIR):
    """Return a list of project names that have stored vaults."""
    if not vault_dir.exists():
        return []
    return [p.stem for p in vault_dir.glob("*.vault")]


def delete_vault(project: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> bool:
    """Delete a project vault. Returns True if deleted, False if not found."""
    path = _vault_path(project, vault_dir)
    if path.exists():
        path.unlink()
        return True
    return False
