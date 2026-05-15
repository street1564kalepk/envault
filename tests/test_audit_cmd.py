"""Tests for the audit command and set_cmd metadata tracking."""

import pytest
from click.testing import CliRunner

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.delete_cmd import delete_var
from envault.commands.audit_cmd import audit_vault, audit_cmd
from envault.store import _vault_path

PROJECT = "audit_test"
PASSWORD = "s3cr3t"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    import envault.store as store
    monkeypatch.setattr(store, "VAULT_DIR", tmp_path)
    return tmp_path


@pytest.fixture()
def initialized_vault(isolated_vault_dir):
    init_vault(PROJECT, PASSWORD)
    return isolated_vault_dir


# ---------------------------------------------------------------------------
# audit_vault
# ---------------------------------------------------------------------------

def test_audit_records_created_on_set(initialized_vault):
    set_var(PROJECT, PASSWORD, "DB_URL", "postgres://localhost/db")
    records = audit_vault(PROJECT, PASSWORD)
    assert len(records) == 1
    rec = records[0]
    assert rec["key"] == "DB_URL"
    assert rec["version"] == 1
    assert rec["created_at"] == rec["updated_at"]


def test_audit_version_increments_on_update(initialized_vault):
    set_var(PROJECT, PASSWORD, "API_KEY", "v1")
    set_var(PROJECT, PASSWORD, "API_KEY", "v2")
    set_var(PROJECT, PASSWORD, "API_KEY", "v3")
    records = audit_vault(PROJECT, PASSWORD)
    assert records[0]["version"] == 3


def test_audit_updated_at_changes_on_update(initialized_vault):
    set_var(PROJECT, PASSWORD, "TOKEN", "first")
    rec_before = audit_vault(PROJECT, PASSWORD, key="TOKEN")[0]
    set_var(PROJECT, PASSWORD, "TOKEN", "second")
    rec_after = audit_vault(PROJECT, PASSWORD, key="TOKEN")[0]
    # updated_at must be >= created_at (both ISO strings, lexicographic compare is fine)
    assert rec_after["updated_at"] >= rec_before["updated_at"]


def test_audit_filter_by_key(initialized_vault):
    set_var(PROJECT, PASSWORD, "A", "1")
    set_var(PROJECT, PASSWORD, "B", "2")
    records = audit_vault(PROJECT, PASSWORD, key="A")
    assert len(records) == 1
    assert records[0]["key"] == "A"


def test_audit_filter_missing_key_raises(initialized_vault):
    set_var(PROJECT, PASSWORD, "A", "1")
    with pytest.raises(KeyError, match="MISSING"):
        audit_vault(PROJECT, PASSWORD, key="MISSING")


def test_audit_nonexistent_vault_raises(isolated_vault_dir):
    with pytest.raises(FileNotFoundError):
        audit_vault("ghost", PASSWORD)


def test_audit_metadata_removed_on_delete(initialized_vault):
    set_var(PROJECT, PASSWORD, "TEMP", "x")
    delete_var(PROJECT, PASSWORD, "TEMP")
    records = audit_vault(PROJECT, PASSWORD)
    assert all(r["key"] != "TEMP" for r in records)


# ---------------------------------------------------------------------------
# audit_cmd (formatted output)
# ---------------------------------------------------------------------------

def test_audit_cmd_text_output(initialized_vault):
    set_var(PROJECT, PASSWORD, "FOO", "bar")
    output = audit_cmd(PROJECT, PASSWORD, key=None, as_json=False)
    assert "FOO" in output
    assert "version" in output


def test_audit_cmd_json_output(initialized_vault):
    import json
    set_var(PROJECT, PASSWORD, "FOO", "bar")
    output = audit_cmd(PROJECT, PASSWORD, key=None, as_json=True)
    parsed = json.loads(output)
    assert isinstance(parsed, list)
    assert parsed[0]["key"] == "FOO"


def test_audit_cmd_empty_vault_message(initialized_vault):
    output = audit_cmd(PROJECT, PASSWORD, key=None, as_json=False)
    assert "No audit records" in output
