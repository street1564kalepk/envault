"""Delete command: remove a variable from a vault and its audit metadata."""

from envault.store import load_vault, save_vault, vault_exists


def delete_var(project: str, password: str, key: str) -> None:
    """Remove *key* from the named vault (including its audit metadata)."""
    if not vault_exists(project):
        raise FileNotFoundError(f"Vault '{project}' does not exist.")

    data = load_vault(project, password)

    if key not in data:
        raise KeyError(f"Key '{key}' not found in vault '{project}'.")

    del data[key]

    # Clean up metadata if present
    meta = data.get("__meta__", {})
    if key in meta:
        del meta[key]
        data["__meta__"] = meta

    save_vault(project, password, data)
