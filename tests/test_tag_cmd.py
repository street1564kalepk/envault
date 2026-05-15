"""Tests for tag management (add / remove / list / filter)."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.commands.tag_cmd import add_tag, list_by_tag, list_tags, remove_tag
from envault.commands.init import init_vault
from envault.commands.set_cmd import set_var

PROJECT = "tagtest"
PASSWORD = "s3cr3t"


@pytest.fixture()
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_with_vars(isolated_vault_dir):
    init_vault(PROJECT, PASSWORD)
    set_var(PROJECT, PASSWORD, "DB_HOST", "localhost")
    set_var(PROJECT, PASSWORD, "DB_PORT", "5432")
    set_var(PROJECT, PASSWORD, "API_KEY", "abc123")
    return isolated_vault_dir


def test_add_tag_success(vault_with_vars):
    entry = add_tag(PROJECT, PASSWORD, "DB_HOST", "database")
    assert "database" in entry["tags"]


def test_add_duplicate_tag_raises(vault_with_vars):
    add_tag(PROJECT, PASSWORD, "DB_HOST", "database")
    with pytest.raises(ValueError, match="already exists"):
        add_tag(PROJECT, PASSWORD, "DB_HOST", "database")


def test_add_tag_missing_key_raises(vault_with_vars):
    with pytest.raises(KeyError, match="MISSING"):
        add_tag(PROJECT, PASSWORD, "MISSING", "sometag")


def test_remove_tag_success(vault_with_vars):
    add_tag(PROJECT, PASSWORD, "DB_PORT", "database")
    entry = remove_tag(PROJECT, PASSWORD, "DB_PORT", "database")
    assert "database" not in entry["tags"]


def test_remove_nonexistent_tag_raises(vault_with_vars):
    with pytest.raises(ValueError, match="not found"):
        remove_tag(PROJECT, PASSWORD, "DB_PORT", "ghost")


def test_list_tags_for_key(vault_with_vars):
    add_tag(PROJECT, PASSWORD, "API_KEY", "sensitive")
    add_tag(PROJECT, PASSWORD, "API_KEY", "external")
    tags = list_tags(PROJECT, PASSWORD, "API_KEY")
    assert tags == ["external", "sensitive"]


def test_list_all_tags_across_vault(vault_with_vars):
    add_tag(PROJECT, PASSWORD, "DB_HOST", "database")
    add_tag(PROJECT, PASSWORD, "API_KEY", "sensitive")
    tags = list_tags(PROJECT, PASSWORD)
    assert "database" in tags
    assert "sensitive" in tags


def test_list_by_tag_returns_matching_keys(vault_with_vars):
    add_tag(PROJECT, PASSWORD, "DB_HOST", "database")
    add_tag(PROJECT, PASSWORD, "DB_PORT", "database")
    add_tag(PROJECT, PASSWORD, "API_KEY", "sensitive")
    result = list_by_tag(PROJECT, PASSWORD, "database")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_list_by_tag_no_matches(vault_with_vars):
    result = list_by_tag(PROJECT, PASSWORD, "nonexistent")
    assert result == {}


def test_multiple_tags_on_same_key(vault_with_vars):
    add_tag(PROJECT, PASSWORD, "API_KEY", "sensitive")
    add_tag(PROJECT, PASSWORD, "API_KEY", "external")
    add_tag(PROJECT, PASSWORD, "API_KEY", "prod")
    tags = list_tags(PROJECT, PASSWORD, "API_KEY")
    assert len(tags) == 3
    assert "prod" in tags
