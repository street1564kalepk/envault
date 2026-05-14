"""CLI entry point for envault."""

import sys
import click
from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.get_cmd import get_var
from envault.commands.list_cmd import list_vars
from envault.commands.delete_cmd import delete_var


@click.group()
@click.version_option(version="0.1.0", prog_name="envault")
def cli():
    """envault — Secure local .env file manager with per-project encryption."""
    pass


cli.add_command(init_vault, name="init")
cli.add_command(set_var, name="set")
cli.add_command(get_var, name="get")
cli.add_command(list_vars, name="list")
cli.add_command(delete_var, name="delete")


def main():
    cli()


if __name__ == "__main__":
    main()
