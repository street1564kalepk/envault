import click
from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.get_cmd import get_var
from envault.commands.list_cmd import list_vars
from envault.commands.delete_cmd import delete_var
from envault.commands.export_cmd import export_vars
from envault.commands.import_cmd import import_vars


def _default_project():
    """Return the current directory name as the default project name."""
    import os
    return os.path.basename(os.getcwd())


@click.group()
def cli():
    """envault — Secure local .env file manager."""
    pass


cli.add_command(init_vault, name="init")
cli.add_command(set_var, name="set")
cli.add_command(get_var, name="get")
cli.add_command(list_vars, name="list")
cli.add_command(delete_var, name="delete")


@cli.command("export")
@click.option("--project", "-p", default=_default_project, show_default=True, help="Project name")
@click.option("--format", "-f", "fmt", default="dotenv", type=click.Choice(["dotenv", "shell", "json"]), show_default=True, help="Output format")
@click.option("--output", "-o", default=None, help="Output file path (stdout if omitted)")
@click.password_option("--password", "-P", confirmation_prompt=False, help="Vault password")
def export_cmd(project, fmt, output, password):
    """Export vault variables to stdout or a file."""
    export_vars(project, password, fmt, output)


@cli.command("import")
@click.argument("filepath")
@click.option("--project", "-p", default=_default_project, show_default=True, help="Project name")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
@click.password_option("--password", "-P", confirmation_prompt=False, help="Vault password")
def import_cmd(filepath, project, overwrite, password):
    """Import variables from a .env file into the vault."""
    import_vars(project, password, filepath, overwrite)


def main():
    cli()


if __name__ == "__main__":
    main()
