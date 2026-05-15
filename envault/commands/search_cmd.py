"""Search for keys or values across one or all vaults."""

from typing import Optional

import click

from envault.store import load_vault, list_vaults, vault_exists
from envault.crypto import decrypt


def search_vars(
    query: str,
    password: str,
    project: str,
    search_values: bool = False,
    case_sensitive: bool = False,
) -> list[dict]:
    """
    Search for keys (and optionally values) in a vault matching *query*.

    Returns a list of dicts with keys: 'project', 'key', 'value'.
    Raises FileNotFoundError if the vault does not exist.
    Raises ValueError if the password is wrong.
    """
    if not vault_exists(project):
        raise FileNotFoundError(f"No vault found for project '{project}'.")

    vault = load_vault(project)
    token = vault["token"]
    salt = bytes.fromhex(vault["salt"])
    data: dict = decrypt(token, password, salt)

    needle = query if case_sensitive else query.lower()
    results = []

    for key, value in data.items():
        hay_key = key if case_sensitive else key.lower()
        hay_val = value if case_sensitive else value.lower()

        matched = needle in hay_key or (search_values and needle in hay_val)
        if matched:
            results.append({"project": project, "key": key, "value": value})

    return results


def search_all_vaults(
    query: str,
    password: str,
    search_values: bool = False,
    case_sensitive: bool = False,
) -> list[dict]:
    """Run search_vars across every known vault, skipping vaults where
    decryption fails (different password)."""
    all_results = []
    for project in list_vaults():
        try:
            results = search_vars(
                query, password, project, search_values, case_sensitive
            )
            all_results.extend(results)
        except (ValueError, KeyError):
            # wrong password for this vault — skip silently
            continue
    return all_results


@click.command("search")
@click.argument("query")
@click.option("--project", "-p", default=None, help="Vault project name (default: cwd name).")
@click.option("--all-vaults", "-a", is_flag=True, help="Search across all vaults.")
@click.option("--values", "-v", is_flag=True, help="Also search inside values.")
@click.option("--case-sensitive", "-c", is_flag=True, help="Case-sensitive matching.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def search_cmd(
    query: str,
    project: Optional[str],
    all_vaults: bool,
    values: bool,
    case_sensitive: bool,
    password: str,
) -> None:
    """Search for QUERY in vault key names (and optionally values)."""
    from envault.cli import _default_project

    if all_vaults:
        results = search_all_vaults(query, password, values, case_sensitive)
    else:
        proj = project or _default_project()
        try:
            results = search_vars(query, password, proj, values, case_sensitive)
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc))
        except ValueError:
            raise click.ClickException("Decryption failed — wrong password?")

    if not results:
        click.echo("No matches found.")
        return

    for hit in results:
        prefix = f"[{hit['project']}] " if all_vaults else ""
        click.echo(f"{prefix}{hit['key']}={hit['value']}")
