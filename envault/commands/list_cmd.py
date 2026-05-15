"""List command: list variables in a vault."""

import click
from envault.store import vault_exists, load_vault


@click.command()
@click.argument("project")
@click.password_option(
    prompt="Master password",
    confirmation_prompt=False,
    help="Master password to decrypt the vault.",
)
@click.option("--show-values", is_flag=True, default=False, help="Show variable values.")
def list_vars(project: str, password: str, show_values: bool):
    """List all variables stored in the PROJECT vault."""
    if not vault_exists(project):
        click.echo(click.style(f"Vault '{project}' does not exist.", fg="red"))
        raise SystemExit(1)

    try:
        data = load_vault(project, password)
    except Exception:
        click.echo(click.style("Invalid password or corrupted vault.", fg="red"))
        raise SystemExit(1)

    if not data:
        click.echo(click.style(f"Vault '{project}' is empty.", fg="yellow"))
        return

    count = len(data)
    click.echo(click.style(f"Variables in vault '{project}' ({count} total):", bold=True))
    for key, value in sorted(data.items()):
        if show_values:
            click.echo(f"  {key}={value}")
        else:
            click.echo(f"  {key}")
