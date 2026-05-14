"""Init command: create a new vault for a project."""

import click
from envault.store import vault_exists, save_vault


@click.command()
@click.argument("project")
@click.password_option(
    prompt="Master password",
    confirmation_prompt="Confirm master password",
    help="Master password to encrypt the vault.",
)
def init_vault(project: str, password: str):
    """Initialize a new encrypted vault for PROJECT."""
    if vault_exists(project):
        click.echo(
            click.style(f"Vault '{project}' already exists.", fg="yellow")
        )
        if not click.confirm("Overwrite existing vault?", default=False):
            click.echo("Aborted.")
            raise SystemExit(0)

    save_vault(project, password, {})
    click.echo(
        click.style(f"✓ Vault '{project}' initialized successfully.", fg="green")
    )
