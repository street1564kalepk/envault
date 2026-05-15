"""Tag management for vault variables — add, remove, and filter by tags."""

from __future__ import annotations

from typing import Optional

from envault.store import load_vault, save_vault


def add_tag(project: str, password: str, key: str, tag: str) -> dict:
    """Add a tag to an existing variable. Returns updated entry."""
    vault = load_vault(project, password)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in project '{project}'.")

    entry = vault[key]
    tags: list[str] = entry.setdefault("tags", [])
    if tag in tags:
        raise ValueError(f"Tag '{tag}' already exists on key '{key}'.")
    tags.append(tag)
    save_vault(project, password, vault)
    return entry


def remove_tag(project: str, password: str, key: str, tag: str) -> dict:
    """Remove a tag from an existing variable. Returns updated entry."""
    vault = load_vault(project, password)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in project '{project}'.")

    entry = vault[key]
    tags: list[str] = entry.get("tags", [])
    if tag not in tags:
        raise ValueError(f"Tag '{tag}' not found on key '{key}'.")
    tags.remove(tag)
    entry["tags"] = tags
    save_vault(project, password, vault)
    return entry


def list_by_tag(project: str, password: str, tag: str) -> dict[str, dict]:
    """Return all variables in *project* that carry *tag*."""
    vault = load_vault(project, password)
    return {k: v for k, v in vault.items() if tag in v.get("tags", [])}


def list_tags(project: str, password: str, key: Optional[str] = None) -> list[str]:
    """List all tags for a specific key, or all unique tags across the vault."""
    vault = load_vault(project, password)
    if key is not None:
        if key not in vault:
            raise KeyError(f"Key '{key}' not found in project '{project}'.")
        return sorted(vault[key].get("tags", []))
    all_tags: set[str] = set()
    for entry in vault.values():
        all_tags.update(entry.get("tags", []))
    return sorted(all_tags)
