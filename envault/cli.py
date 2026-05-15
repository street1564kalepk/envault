"""CLI entry point for envault."""
from __future__ import annotations

import os

import click

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.get_cmd import get_var
from envault.commands.list_cmd import list_vars
from envault.commands.delete_cmd import delete_var
from envault.commands.export_cmd import export_cmd
from envault.commands.import_cmd import import_cmd
from envault.commands.rotate_cmd import rotate_cmd
from envault.commands.copy_cmd import copy_cmd
from envault.commands.rename_cmd import rename_cmd
from envault.commands.diff_cmd import diff_cmd


def _default_project() -> str:
    return os.path.basename(os.getcwd())


@click.group()
def cli():
    """envault — Secure local .env manager."""


@cli.command("init")
@click.argument("project", default=None, required=False)
@click.password_option(help="Master password for the vault.")
def init_cmd(project, password):
    """Initialise a new vault for PROJECT (default: cwd name)."""
    project = project or _default_project()
    try:
        init_vault(project, password)
        click.echo(f"Vault '{project}' created.")
    except FileExistsError as exc:
        raise click.ClickException(str(exc))


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("-p", "--project", default=None)
@click.password_option(confirmation_prompt=False)
def set_cmd(key, value, project, password):
    """Set KEY=VALUE in the vault."""
    project = project or _default_project()
    try:
        set_var(project, password, key, value)
        click.echo(f"Set {key} in '{project}'.")
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command("get")
@click.argument("key")
@click.option("-p", "--project", default=None)
@click.password_option(confirmation_prompt=False)
def get_cmd(key, project, password):
    """Get the value of KEY from the vault."""
    project = project or _default_project()
    try:
        value = get_var(project, password, key)
        click.echo(value)
    except Exception as exc:
        raise click.ClickException(str(exc))


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(copy_cmd, "copy")
cli.add_command(rename_cmd, "rename")
cli.add_command(diff_cmd, "diff")


if __name__ == "__main__":
    cli()
