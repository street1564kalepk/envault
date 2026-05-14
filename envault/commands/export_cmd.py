import click
import os
from envault.store import load_vault, vault_exists, _vault_path
from envault.crypto import decrypt


def export_vars(project: str, password: str, format: str, output: str | None) -> None:
    """
    Export all variables from a vault in the specified format.
    Supported formats: dotenv, shell, json
    """
    if not vault_exists(project):
        click.echo(f"No vault found for project '{project}'. Run 'envault init' first.", err=True)
        raise SystemExit(1)

    try:
        vault_data = load_vault(project)
        variables = vault_data.get("variables", {})

        if not variables:
            click.echo(f"No variables found in vault '{project}'.")
            return

        decrypted = {}
        for key, token in variables.items():
            decrypted[key] = decrypt(token, password)

        lines = _format_export(decrypted, format)
        content = "\n".join(lines) + "\n"

        if output:
            with open(output, "w") as f:
                f.write(content)
            click.echo(f"Exported {len(decrypted)} variable(s) to '{output}'.")
        else:
            click.echo(content, nl=False)

    except Exception as e:
        click.echo(f"Error exporting variables: {e}", err=True)
        raise SystemExit(1)


def _format_export(variables: dict, format: str) -> list[str]:
    if format == "dotenv":
        return [f"{k}={v}" for k, v in variables.items()]
    elif format == "shell":
        return [f"export {k}={v}" for k, v in variables.items()]
    elif format == "json":
        import json
        return [json.dumps(variables, indent=2)]
    else:
        raise ValueError(f"Unsupported format: {format}")
