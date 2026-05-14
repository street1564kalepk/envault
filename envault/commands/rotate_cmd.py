"""Command to rotate the master password for a vault."""

import click
from envault.store import load_vault, save_vault, vault_exists
from envault.crypto import decrypt, encrypt, derive_key


def rotate_password(project: str, old_password: str, new_password: str) -> int:
    """Re-encrypt all vault entries with a new master password.

    Args:
        project: The project name whose vault password should be rotated.
        old_password: The current master password.
        new_password: The new master password to use.

    Returns:
        The number of variables that were re-encrypted.

    Raises:
        click.ClickException: If the vault does not exist or decryption fails.
    """
    if not vault_exists(project):
        raise click.ClickException(f"No vault found for project '{project}'.")

    try:
        vault = load_vault(project, old_password)
    except Exception:
        raise click.ClickException(
            "Failed to unlock vault. Check that the old password is correct."
        )

    # vault already decrypted by load_vault; re-save under new password
    count = len(vault)
    save_vault(project, vault, new_password)
    return count


@click.command("rotate")
@click.argument("project")
@click.option(
    "--old-password",
    prompt="Current master password",
    hide_input=True,
    help="The current master password for the vault.",
)
@click.option(
    "--new-password",
    prompt="New master password",
    hide_input=True,
    confirmation_prompt="Confirm new master password",
    help="The new master password to encrypt the vault with.",
)
def rotate_cmd(project: str, old_password: str, new_password: str) -> None:
    """Rotate the master password for PROJECT's vault."""
    if old_password == new_password:
        raise click.ClickException("New password must differ from the old password.")

    count = rotate_password(project, old_password, new_password)
    click.echo(
        f"Password rotated successfully. {count} variable(s) re-encrypted for '{project}'."
    )
