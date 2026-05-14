import click
import os
from envault.store import load_vault, save_vault, vault_exists
from envault.crypto import encrypt


def import_vars(project: str, password: str, filepath: str, overwrite: bool) -> None:
    """
    Import variables from a .env file into the vault.
    Skips blank lines and comments (lines starting with #).
    """
    if not vault_exists(project):
        click.echo(f"No vault found for project '{project}'. Run 'envault init' first.", err=True)
        raise SystemExit(1)

    if not os.path.exists(filepath):
        click.echo(f"File not found: '{filepath}'", err=True)
        raise SystemExit(1)

    parsed = _parse_dotenv(filepath)
    if not parsed:
        click.echo("No valid variables found in the file.")
        return

    vault_data = load_vault(project)
    variables = vault_data.get("variables", {})

    imported = 0
    skipped = 0
    for key, value in parsed.items():
        if key in variables and not overwrite:
            click.echo(f"Skipping '{key}' (already exists). Use --overwrite to replace.")
            skipped += 1
            continue
        variables[key] = encrypt(value, password)
        imported += 1

    vault_data["variables"] = variables
    save_vault(project, vault_data)

    click.echo(f"Imported {imported} variable(s) into vault '{project}'" +
               (f", skipped {skipped}." if skipped else "."))


def _parse_dotenv(filepath: str) -> dict:
    result = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                result[key] = value
    return result
