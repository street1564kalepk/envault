"""Tests for snapshot create / restore / delete / list logic."""

import pytest

from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var
from envault.commands.snapshot_cmd import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)
from envault.store import _vault_path, load_vault

PROJECT = "snap_test"
PASSWORD = "s3cr3t"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def initialized_vault(isolated_vault_dir):
    init_vault(PROJECT, PASSWORD)
    set_var(PROJECT, PASSWORD, "FOO", "bar")
    set_var(PROJECT, PASSWORD, "BAZ", "qux")
    return isolated_vault_dir


def test_create_snapshot_success(initialized_vault):
    snap = create_snapshot(PROJECT, PASSWORD, "v1")
    assert "created_at" in snap
    assert snap["variables"]["FOO"]["value"] == "bar"
    assert snap["variables"]["BAZ"]["value"] == "qux"


def test_create_duplicate_snapshot_raises(initialized_vault):
    create_snapshot(PROJECT, PASSWORD, "v1")
    with pytest.raises(ValueError, match="already exists"):
        create_snapshot(PROJECT, PASSWORD, "v1")


def test_create_snapshot_nonexistent_vault_raises(isolated_vault_dir):
    with pytest.raises(FileNotFoundError):
        create_snapshot("ghost", PASSWORD, "v1")


def test_list_snapshots_empty(initialized_vault):
    snaps = list_snapshots(PROJECT, PASSWORD)
    assert snaps == {}


def test_list_snapshots_after_create(initialized_vault):
    create_snapshot(PROJECT, PASSWORD, "v1")
    create_snapshot(PROJECT, PASSWORD, "v2")
    snaps = list_snapshots(PROJECT, PASSWORD)
    assert set(snaps.keys()) == {"v1", "v2"}
    assert snaps["v1"]["count"] == 2


def test_restore_snapshot_overwrites_current(initialized_vault):
    create_snapshot(PROJECT, PASSWORD, "v1")
    # Change FOO after snapshot
    set_var(PROJECT, PASSWORD, "FOO", "changed")
    set_var(PROJECT, PASSWORD, "NEW_KEY", "new_val")

    count = restore_snapshot(PROJECT, PASSWORD, "v1")
    assert count == 2

    data = load_vault(PROJECT, PASSWORD)
    assert data["FOO"]["value"] == "bar"
    # NEW_KEY added after snapshot still exists (restore merges, not wipes)
    assert "NEW_KEY" in data


def test_restore_missing_snapshot_raises(initialized_vault):
    with pytest.raises(KeyError, match="not found"):
        restore_snapshot(PROJECT, PASSWORD, "ghost")


def test_delete_snapshot_success(initialized_vault):
    create_snapshot(PROJECT, PASSWORD, "v1")
    delete_snapshot(PROJECT, PASSWORD, "v1")
    snaps = list_snapshots(PROJECT, PASSWORD)
    assert "v1" not in snaps


def test_delete_missing_snapshot_raises(initialized_vault):
    with pytest.raises(KeyError, match="not found"):
        delete_snapshot(PROJECT, PASSWORD, "nonexistent")


def test_snapshots_not_exposed_as_variables(initialized_vault):
    create_snapshot(PROJECT, PASSWORD, "v1")
    data = load_vault(PROJECT, PASSWORD)
    # __snapshots__ should be present but not a user variable
    assert "__snapshots__" in data
    snaps = list_snapshots(PROJECT, PASSWORD)
    for name in snaps:
        assert not name.startswith("__")
