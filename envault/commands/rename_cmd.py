"""Rename a variable key within a vault."""

import click
from envault.store import load_vault, save_vault, vault_exists


def rename_var(project: str, password: str, old_key: str, new_key: str) -> None:
    """
    Rename an existing variable key in the vault.

    Raises:
        FileNotFoundError: If the vault does not exist.
        KeyError: If old_key does not exist or new_key already exists.
    """
    if not vault_exists(project):
        raise FileNotFoundError(f"No vault found for project '{project}'.")

    data = load_vault(project, password)

    if old_key not in data:
        raise KeyError(f"Variable '{old_key}' does not exist in vault '{project}'.")

    if new_key in data:
        raise KeyError(
            f"Variable '{new_key}' already exists in vault '{project}'. "
            "Remove it first or choose a different name."
        )

    data[new_key] = data.pop(old_key)
    save_vault(project, password, data)


@click.command("rename")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--project", "-p", default=None, help="Project name (default: current directory name).")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False, help="Vault password.")
def rename_cmd(old_key: str, new_key: str, project: str, password: str) -> None:
    """Rename a variable OLD_KEY to NEW_KEY in the vault."""
    from envault.cli import _default_project

    project = project or _default_project()

    try:
        rename_var(project, password, old_key, new_key)
        click.echo(f"Renamed '{old_key}' -> '{new_key}' in vault '{project}'.")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
