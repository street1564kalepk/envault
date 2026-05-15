"""CLI bindings for snapshot commands."""

import click

from envault.cli import _default_project
from envault.commands.snapshot_cmd import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)


@click.group("snapshot")
def snapshot_group():
    """Manage named snapshots of vault variables."""


@snapshot_group.command("create")
@click.argument("name")
@click.option("--project", "-p", default=None, help="Project name (default: cwd name).")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def snapshot_create_cmd(name: str, project: str, password: str):
    """Create a snapshot NAME of the current vault state."""
    project = project or _default_project()
    try:
        snap = create_snapshot(project, password, name)
        click.echo(f"Snapshot '{name}' created at {snap['created_at']}.")
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc))


@snapshot_group.command("restore")
@click.argument("name")
@click.option("--project", "-p", default=None)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def snapshot_restore_cmd(name: str, project: str, password: str):
    """Restore vault variables from snapshot NAME."""
    project = project or _default_project()
    try:
        count = restore_snapshot(project, password, name)
        click.echo(f"Restored {count} variable(s) from snapshot '{name}'.")
    except (FileNotFoundError, KeyError) as exc:
        raise click.ClickException(str(exc))


@snapshot_group.command("delete")
@click.argument("name")
@click.option("--project", "-p", default=None)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def snapshot_delete_cmd(name: str, project: str, password: str):
    """Delete snapshot NAME."""
    project = project or _default_project()
    try:
        delete_snapshot(project, password, name)
        click.echo(f"Snapshot '{name}' deleted.")
    except (FileNotFoundError, KeyError) as exc:
        raise click.ClickException(str(exc))


@snapshot_group.command("list")
@click.option("--project", "-p", default=None)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def snapshot_list_cmd(project: str, password: str):
    """List all snapshots for the vault."""
    project = project or _default_project()
    try:
        snaps = list_snapshots(project, password)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    if not snaps:
        click.echo("No snapshots found.")
        return

    for name, meta in snaps.items():
        click.echo(f"  {name}  ({meta['count']} vars)  created: {meta['created_at']}")
