"""Copy variables between vaults (projects)."""

import click
from envault.store import load_vault, save_vault, vault_exists
from envault.crypto import decrypt, encrypt


def copy_vars(src_project: str, dst_project: str, src_password: str,
             dst_password: str, keys: tuple, overwrite: bool = False) -> dict:
    """
    Copy environment variables from one vault to another.

    Args:
        src_project: Source project name.
        dst_project: Destination project name.
        src_password: Password for the source vault.
        dst_password: Password for the destination vault.
        keys: Tuple of variable names to copy. If empty, copies all.
        overwrite: Whether to overwrite existing keys in destination.

    Returns:
        A dict mapping copied key names to their plaintext values.
    """
    if not vault_exists(src_project):
        raise click.ClickException(f"Source vault '{src_project}' does not exist.")
    if not vault_exists(dst_project):
        raise click.ClickException(f"Destination vault '{dst_project}' does not exist.")

    src_vault = load_vault(src_project)
    dst_vault = load_vault(dst_project)

    src_salt = src_vault["salt"]
    dst_salt = dst_vault["salt"]
    src_vars = src_vault.get("vars", {})
    dst_vars = dst_vault.get("vars", {})

    candidates = keys if keys else tuple(src_vars.keys())
    copied = {}

    for key in candidates:
        if key not in src_vars:
            raise click.ClickException(f"Key '{key}' not found in source vault '{src_project}'.")
        if key in dst_vars and not overwrite:
            click.echo(f"Skipping '{key}': already exists in destination (use --overwrite to replace).")
            continue

        plaintext = decrypt(src_vars[key], src_password, src_salt)
        dst_vars[key] = encrypt(plaintext, dst_password, dst_salt)
        copied[key] = plaintext

    dst_vault["vars"] = dst_vars
    save_vault(dst_project, dst_vault)
    return copied


@click.command("copy")
@click.argument("src_project")
@click.argument("dst_project")
@click.option("--key", "-k", multiple=True, help="Specific key(s) to copy. Omit to copy all.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def copy_cmd(src_project, dst_project, key, overwrite):
    """Copy variables from SRC_PROJECT vault to DST_PROJECT vault."""
    src_password = click.prompt(f"Password for '{src_project}'", hide_input=True)
    dst_password = click.prompt(f"Password for '{dst_project}'", hide_input=True)

    copied = copy_vars(src_project, dst_project, src_password, dst_password,
                       keys=key, overwrite=overwrite)

    if copied:
        click.echo(f"Copied {len(copied)} variable(s) from '{src_project}' to '{dst_project}':")
        for k in copied:
            click.echo(f"  {k}")
    else:
        click.echo("No variables were copied.")
