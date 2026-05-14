"""Get command: retrieve a variable from a vault."""

import click
from envault.store import vault_exists, load_vault


@click.command()
@click.argument("project")
@click.argument("key")
@click.password_option(
    prompt="Master password",
    confirmation_prompt=False,
    help="Master password to decrypt the vault.",
)
@click.option("--export", is_flag=True, default=False, help="Print as export statement.")
@click.option("--shell-quote", is_flag=True, default=False, help="Shell-escape the value in export statements.")
def get_var(project: str, key: str, password: str, export: bool, shell_quote: bool):
    """Get the value of KEY from the PROJECT vault."""
    if not vault_exists(project):
        click.echo(
            click.style(f"Vault '{project}' does not exist.", fg="red")
        )
        raise SystemExit(1)

    try:
        data = load_vault(project, password)
    except Exception:
        click.echo(click.style("Invalid password or corrupted vault.", fg="red"))
        raise SystemExit(1)

    if key not in data:
        click.echo(click.style(f"Key '{key}' not found in vault '{project}'.", fg="yellow"))
        raise SystemExit(1)

    value = data[key]
    if export:
        if shell_quote:
            import shlex
            value = shlex.quote(value)
        click.echo(f"export {key}={value}")
    else:
        click.echo(value)
