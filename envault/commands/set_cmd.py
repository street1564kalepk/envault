"""Set command: add or update a variable in a vault."""

import click
from envault.store import vault_exists, load_vault, save_vault


@click.command()
@click.argument("project")
@click.argument("key")
@click.argument("value")
@click.password_option(
    prompt="Master password",
    confirmation_prompt=False,
    help="Master password to decrypt/encrypt the vault.",
)
def set_var(project: str, key: str, value: str, password: str):
    """Set KEY=VALUE in the PROJECT vault."""
    if not vault_exists(project):
        click.echo(
            click.style(
                f"Vault '{project}' does not exist. Run 'envault init {project}' first.",
                fg="red",
            )
        )
        raise SystemExit(1)

    try:
        data = load_vault(project, password)
    except Exception:
        click.echo(click.style("Invalid password or corrupted vault.", fg="red"))
        raise SystemExit(1)

    action = "Updated" if key in data else "Set"
    data[key] = value
    save_vault(project, password, data)
    click.echo(click.style(f"✓ {action} '{key}' in vault '{project}'.", fg="green"))
