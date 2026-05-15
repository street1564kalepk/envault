"""CLI wiring for tag sub-commands."""

from __future__ import annotations

import click

from envault.cli import _default_project
from envault.commands.tag_cmd import add_tag, list_by_tag, list_tags, remove_tag


@click.group("tag")
def tag_group() -> None:
    """Manage tags on vault variables."""


@tag_group.command("add")
@click.argument("key")
@click.argument("tag")
@click.option("-p", "--project", default=None, help="Project name.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def tag_add_cmd(key: str, tag: str, project: str | None, password: str) -> None:
    """Add TAG to KEY in the vault."""
    project = project or _default_project()
    try:
        add_tag(project, password, key, tag)
        click.echo(f"Tag '{tag}' added to '{key}'.")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@tag_group.command("remove")
@click.argument("key")
@click.argument("tag")
@click.option("-p", "--project", default=None, help="Project name.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def tag_remove_cmd(key: str, tag: str, project: str | None, password: str) -> None:
    """Remove TAG from KEY in the vault."""
    project = project or _default_project()
    try:
        remove_tag(project, password, key, tag)
        click.echo(f"Tag '{tag}' removed from '{key}'.")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@tag_group.command("list")
@click.option("-k", "--key", default=None, help="Limit to a specific key.")
@click.option("-p", "--project", default=None, help="Project name.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def tag_list_cmd(key: str | None, project: str | None, password: str) -> None:
    """List all tags (optionally for a specific KEY)."""
    project = project or _default_project()
    try:
        tags = list_tags(project, password, key)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    if tags:
        click.echo("\n".join(tags))
    else:
        click.echo("No tags found.")


@tag_group.command("filter")
@click.argument("tag")
@click.option("-p", "--project", default=None, help="Project name.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def tag_filter_cmd(tag: str, project: str | None, password: str) -> None:
    """Show all variables that carry TAG."""
    project = project or _default_project()
    matches = list_by_tag(project, password, tag)
    if not matches:
        click.echo(f"No variables tagged '{tag}'.")
        return
    for k in sorted(matches):
        click.echo(k)
