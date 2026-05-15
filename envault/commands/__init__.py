"""envault command modules package."""

from envault.commands.audit_cmd import audit_cmd, audit_vault
from envault.commands.copy_cmd import copy_cmd, copy_vars
from envault.commands.delete_cmd import delete_var
from envault.commands.diff_cmd import diff_cmd, diff_vaults
from envault.commands.export_cmd import export_vars
from envault.commands.get_cmd import get_var
from envault.commands.import_cmd import import_vars
from envault.commands.init import init_vault
from envault.commands.list_cmd import list_vars
from envault.commands.rename_cmd import rename_cmd, rename_var
from envault.commands.rotate_cmd import rotate_cmd, rotate_password
from envault.commands.search_cmd import search_all_vaults, search_cmd, search_vars
from envault.commands.set_cmd import set_var
from envault.commands.snapshot_cmd import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)
from envault.commands.tag_cmd import add_tag, list_by_tag, list_tags, remove_tag

__all__ = [
    "audit_cmd",
    "audit_vault",
    "copy_cmd",
    "copy_vars",
    "delete_var",
    "diff_cmd",
    "diff_vaults",
    "export_vars",
    "get_var",
    "import_vars",
    "init_vault",
    "list_vars",
    "rename_cmd",
    "rename_var",
    "rotate_cmd",
    "rotate_password",
    "search_all_vaults",
    "search_cmd",
    "search_vars",
    "set_var",
    "create_snapshot",
    "delete_snapshot",
    "list_snapshots",
    "restore_snapshot",
    "add_tag",
    "list_by_tag",
    "list_tags",
    "remove_tag",
]
