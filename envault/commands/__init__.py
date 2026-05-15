"""envault.commands package — re-exports all command functions for convenience."""

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.get_cmd import get_var
from envault.commands.list_cmd import list_vars
from envault.commands.delete_cmd import delete_var
from envault.commands.export_cmd import export_vars
from envault.commands.import_cmd import import_vars
from envault.commands.rotate_cmd import rotate_password
from envault.commands.copy_cmd import copy_vars
from envault.commands.rename_cmd import rename_var
from envault.commands.diff_cmd import diff_vaults
from envault.commands.search_cmd import search_vars, search_all_vaults
from envault.commands.audit_cmd import audit_vault
from envault.commands.tag_cmd import add_tag, remove_tag, list_by_tag, list_tags
from envault.commands.snapshot_cmd import (
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
    list_snapshots,
)
from envault.commands.env_cmd import run_with_env

__all__ = [
    "init_vault",
    "set_var",
    "get_var",
    "list_vars",
    "delete_var",
    "export_vars",
    "import_vars",
    "rotate_password",
    "copy_vars",
    "rename_var",
    "diff_vaults",
    "search_vars",
    "search_all_vaults",
    "audit_vault",
    "add_tag",
    "remove_tag",
    "list_by_tag",
    "list_tags",
    "create_snapshot",
    "restore_snapshot",
    "delete_snapshot",
    "list_snapshots",
    "run_with_env",
]
