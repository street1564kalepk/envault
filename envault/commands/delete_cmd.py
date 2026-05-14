"""Delete command: remove a variable from a vault."""

import click
from envault.store import vault_exists, load_vault, save_vault


@click.command()
@click.argument("project")
@click.argument("key")
@click.password_option(
    prompt="Master password",
    confirmation_prompt=False,
    help="Master password to decrypt/encrypt the vault.",
)
@click.option("--yes", is_flag=True, default=False, help="Skip confirmation prompt.")
def delete_var(project: str, key: str, password: str, yes: bool):
    """Delete KEY from the PROJECT vault."""
    if not vault_exists(project):
        click.echo(click.style(f"Vault '{project}' does not exist.", fg="red"))
        raise SystemExit(1)

    try:
        data = load_vault(project, password)
    except Exception:
        click.echo(click.style("Invalid password or corrupted vault.", fg="red"))
        raise SystemExit(1)

    if key not in data:
        click.echo(click.style(f"Key '{key}' not found in vault '{project}'.", fg="yellow"))
        raise SystemExit(1)

    if not yes and not click.confirm(f"Delete '{key}' from vault '{project}'?", default=False):
        click.echo("Aborted.")
        raise SystemExit(0)

    del data[key]
    save_vault(project, password, data)
    click.echo(click.style(f"✓ Deleted '{key}' from vault '{project}'.", fg="green"))
