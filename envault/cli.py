"""Entry point for the envault CLI."""

import os

import click

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.get_cmd import get_var
from envault.commands.list_cmd import list_vars
from envault.commands.delete_cmd import delete_var
from envault.commands.export_cmd import export_vars, _format_export
from envault.commands.import_cmd import import_vars
from envault.commands.rotate_cmd import rotate_cmd
from envault.commands.copy_cmd import copy_cmd
from envault.commands.rename_cmd import rename_cmd


def _default_project() -> str:
    """Return the current directory name as the default project identifier."""
    return os.path.basename(os.getcwd())


@click.group()
def cli() -> None:
    """envault — Secure local .env file manager."""


@cli.command("init")
@click.option("--project", "-p", default=None, help="Project name.")
@click.password_option(prompt="New vault password", help="Password to encrypt the vault.")
def init_cmd(project: str, password: str) -> None:
    """Initialise a new vault for the project."""
    project = project or _default_project()
    try:
        init_vault(project, password)
        click.echo(f"Vault '{project}' initialised.")
    except FileExistsError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cli.command("export")
@click.option("--project", "-p", default=None)
@click.option("--format", "fmt", type=click.Choice(["dotenv", "shell"]), default="dotenv")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def export_cmd(project: str, fmt: str, password: str) -> None:
    """Export all variables from the vault."""
    project = project or _default_project()
    data = export_vars(project, password)
    click.echo(_format_export(data, fmt))


@cli.command("import")
@click.argument("dotenv_file", type=click.Path(exists=True))
@click.option("--project", "-p", default=None)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def import_cmd(dotenv_file: str, project: str, password: str) -> None:
    """Import variables from a .env file into the vault."""
    project = project or _default_project()
    count = import_vars(project, password, dotenv_file)
    click.echo(f"Imported {count} variable(s) into vault '{project}'.")


cli.add_command(rotate_cmd)
cli.add_command(copy_cmd)
cli.add_command(rename_cmd)


def main() -> None:  # pragma: no cover
    cli()
