"""envault commands package.

Exposes all command modules for convenient import and CLI registration.
"""

from envault.commands.audit_cmd import audit_cmd
from envault.commands.copy_cmd import copy_cmd
from envault.commands.delete_cmd import delete_var
from envault.commands.diff_cmd import diff_cmd
from envault.commands.export_cmd import export_vars
from envault.commands.get_cmd import get_var
from envault.commands.import_cmd import import_vars
from envault.commands.init import init_vault
from envault.commands.list_cmd import list_vars
from envault.commands.rename_cmd import rename_cmd
from envault.commands.rotate_cmd import rotate_cmd
from envault.commands.search_cmd import search_cmd
from envault.commands.set_cmd import set_var
from envault.commands.tag_cli import tag_group

__all__ = [
    "audit_cmd",
    "copy_cmd",
    "delete_var",
    "diff_cmd",
    "export_vars",
    "get_var",
    "import_vars",
    "init_vault",
    "list_vars",
    "rename_cmd",
    "rotate_cmd",
    "search_cmd",
    "set_var",
    "tag_group",
]
