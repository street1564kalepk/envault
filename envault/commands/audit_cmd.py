"""Audit command: show metadata and access history for vault entries."""

from datetime import datetime, timezone
from typing import Optional

from envault.store import load_vault, vault_exists, _vault_path


def audit_vault(project: str, password: str, key: Optional[str] = None) -> list[dict]:
    """Return audit records for a vault (optionally filtered by key).

    Each record contains:
      - key: variable name
      - created_at: ISO timestamp when the variable was first set
      - updated_at: ISO timestamp of the last update
      - version: number of times the value has been written
    """
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)
    meta = data.get("__meta__", {})

    records = []
    for k, entry in meta.items():
        if key and k != key:
            continue
        records.append(
            {
                "key": k,
                "created_at": entry.get("created_at", "unknown"),
                "updated_at": entry.get("updated_at", "unknown"),
                "version": entry.get("version", 1),
            }
        )

    if key and not records:
        raise KeyError(f"Key '{key}' not found in vault '{project}'.")

    return sorted(records, key=lambda r: r["key"])


def audit_cmd(project: str, password: str, key: Optional[str], as_json: bool) -> str:
    """Format audit results for CLI output."""
    records = audit_vault(project, password, key)

    if not records:
        return f"No audit records found for vault '{project}'."

    if as_json:
        import json
        return json.dumps(records, indent=2)

    lines = [f"Audit for vault '{project}':", ""]
    for rec in records:
        lines.append(f"  {rec['key']}")
        lines.append(f"    created : {rec['created_at']}")
        lines.append(f"    updated : {rec['updated_at']}")
        lines.append(f"    version : {rec['version']}")
        lines.append("")
    return "\n".join(lines).rstrip()
