"""CLI entry-point for the `envault env` command."""

import sys
import click

from envault.commands.env_cmd import run_with_env


@click.command(
    name="env",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option("-p", "--project", default=None, help="Project / vault name.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    help="Master password for the vault.",
)
@click.option(
    "--no-override",
    is_flag=True,
    default=False,
    help="Do not overwrite variables already present in the shell.",
)
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def env_cmd(ctx, project, password, no_override, command):
    """Run COMMAND with vault variables injected into the environment.

    Example:

      envault env --project myapp -- python manage.py runserver
    """
    from envault.cli import _default_project  # lazy import avoids circular dep

    project = project or _default_project()

    if not project:
        raise click.UsageError(
            "No project specified. Use --project or run inside a project directory."
        )

    if not command:
        raise click.UsageError("COMMAND must not be empty.")

    try:
        exit_code = run_with_env(
            project=project,
            password=password,
            command=list(command),
            override=not no_override,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))
    except PermissionError as exc:
        raise click.ClickException(str(exc))

    sys.exit(exit_code)
