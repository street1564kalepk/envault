"""Snapshot command: save and restore named snapshots of a vault's variables."""

from datetime import datetime, timezone
from typing import Optional

from envault.store import load_vault, save_vault, vault_exists


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_snapshot(project: str, password: str, snapshot_name: str) -> dict:
    """Save a named snapshot of the current vault variables."""
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)
    snapshots = data.setdefault("__snapshots__", {})

    if snapshot_name in snapshots:
        raise ValueError(f"Snapshot '{snapshot_name}' already exists. Delete it first.")

    variables = {k: v for k, v in data.items() if not k.startswith("__")}
    snapshots[snapshot_name] = {
        "created_at": _now_iso(),
        "variables": variables,
    }

    save_vault(project, password, data)
    return snapshots[snapshot_name]


def restore_snapshot(project: str, password: str, snapshot_name: str) -> int:
    """Restore variables from a named snapshot. Returns count of restored vars."""
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)
    snapshots = data.get("__snapshots__", {})

    if snapshot_name not in snapshots:
        raise KeyError(f"Snapshot '{snapshot_name}' not found.")

    snapshot_vars = snapshots[snapshot_name]["variables"]
    for key, entry in snapshot_vars.items():
        data[key] = entry

    save_vault(project, password, data)
    return len(snapshot_vars)


def delete_snapshot(project: str, password: str, snapshot_name: str) -> None:
    """Delete a named snapshot."""
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)
    snapshots = data.get("__snapshots__", {})

    if snapshot_name not in snapshots:
        raise KeyError(f"Snapshot '{snapshot_name}' not found.")

    del snapshots[snapshot_name]
    save_vault(project, password, data)


def list_snapshots(project: str, password: str) -> dict:
    """Return all snapshots metadata (name -> created_at, variable count)."""
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)
    snapshots = data.get("__snapshots__", {})
    return {
        name: {
            "created_at": snap["created_at"],
            "count": len(snap["variables"]),
        }
        for name, snap in snapshots.items()
    }
