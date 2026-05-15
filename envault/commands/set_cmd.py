"""Set command: write a variable into a vault, updating audit metadata."""

from datetime import datetime, timezone

from envault.store import load_vault, save_vault, vault_exists


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def set_var(project: str, password: str, key: str, value: str) -> None:
    """Set *key* to *value* in the named vault, creating audit metadata."""
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)

    # Ensure metadata bucket exists
    if "__meta__" not in data:
        data["__meta__"] = {}

    now = _now_iso()
    if key in data.get("__meta__", {}):
        entry = data["__meta__"][key]
        entry["updated_at"] = now
        entry["version"] = entry.get("version", 1) + 1
    else:
        data["__meta__"][key] = {
            "created_at": now,
            "updated_at": now,
            "version": 1,
        }

    data[key] = value
    save_vault(project, password, data)
