"""Diff command: compare variables between two vaults."""
from __future__ import annotations

from typing import Optional

import click

from envault.store import load_vault, vault_exists
from envault.crypto import decrypt


def diff_vaults(
    project_a: str,
    password_a: str,
    project_b: str,
    password_b: str,
    show_values: bool = False,
) -> dict:
    """Compare variables between two vaults.

    Returns a dict with keys:
      - 'only_in_a': keys present only in project_a
      - 'only_in_b': keys present only in project_b
      - 'different': keys present in both but with different values
      - 'same': keys present in both with identical values
    """
    if not vault_exists(project_a):
        raise FileNotFoundError(f"Vault '{project_a}' does not exist.")
    if not vault_exists(project_b):
        raise FileNotFoundError(f"Vault '{project_b}' does not exist.")

    data_a = load_vault(project_a)
    data_b = load_vault(project_b)

    vars_a = {
        k: decrypt(v, password_a)
        for k, v in data_a.get("vars", {}).items()
    }
    vars_b = {
        k: decrypt(v, password_b)
        for k, v in data_b.get("vars", {}).items()
    }

    keys_a = set(vars_a)
    keys_b = set(vars_b)

    only_in_a = sorted(keys_a - keys_b)
    only_in_b = sorted(keys_b - keys_a)
    common = keys_a & keys_b
    different = sorted(k for k in common if vars_a[k] != vars_b[k])
    same = sorted(k for k in common if vars_a[k] == vars_b[k])

    result = {
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "different": different,
        "same": same,
    }
    if show_values:
        result["values_a"] = vars_a
        result["values_b"] = vars_b
    return result


@click.command("diff")
@click.argument("project_a")
@click.argument("project_b")
@click.password_option("-p", "--password-a", prompt="Password for project A",
                       confirmation_prompt=False, help="Password for project A.")
@click.password_option("-q", "--password-b", prompt="Password for project B",
                       confirmation_prompt=False, help="Password for project B.")
@click.option("--show-values", is_flag=True, default=False,
              help="Show differing values side by side.")
def diff_cmd(project_a, project_b, password_a, password_b, show_values):
    """Show differences between two vaults."""
    try:
        result = diff_vaults(project_a, password_a, project_b, password_b,
                             show_values=show_values)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:
        raise click.ClickException(f"Failed to diff vaults: {exc}")

    if result["only_in_a"]:
        click.echo(f"Only in '{project_a}':")
        for k in result["only_in_a"]:
            click.echo(f"  < {k}")

    if result["only_in_b"]:
        click.echo(f"Only in '{project_b}':")
        for k in result["only_in_b"]:
            click.echo(f"  > {k}")

    if result["different"]:
        click.echo("Different values:")
        for k in result["different"]:
            if show_values:
                va = result["values_a"][k]
                vb = result["values_b"][k]
                click.echo(f"  ~ {k}: '{va}' -> '{vb}'")
            else:
                click.echo(f"  ~ {k}")

    if not result["only_in_a"] and not result["only_in_b"] and not result["different"]:
        click.echo("Vaults are identical.")
    else:
        same_count = len(result["same"])
        click.echo(f"({same_count} key(s) identical)")
