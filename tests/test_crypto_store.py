"""Tests for envault crypto and store modules."""

import pytest
from pathlib import Path
from envault.crypto import encrypt, decrypt
from envault.store import (
    save_vault, load_vault, vault_exists, list_vaults, delete_vault
)

# ---------------------------------------------------------------------------
# Crypto tests
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    plaintext = "SECRET=hello\nDB_URL=postgres://localhost/mydb"
    password = "s3cur3P@ss"
    token = encrypt(plaintext, password)
    assert token != plaintext
    result = decrypt(token, password)
    assert result == plaintext


def test_encrypt_produces_different_tokens():
    """Each encryption call should produce a unique token (random salt/nonce)."""
    password = "pw"
    t1 = encrypt("data", password)
    t2 = encrypt("data", password)
    assert t1 != t2


def test_decrypt_wrong_password_raises():
    token = encrypt("secret", "correct")
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong")


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError):
        decrypt("notavalidtoken!!", "password")


# ---------------------------------------------------------------------------
# Store tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path / "vaults"


def test_save_and_load_vault(tmp_vault_dir):
    env_vars = {"API_KEY": "abc123", "DEBUG": "true"}
    save_vault("myproject", env_vars, "pass", vault_dir=tmp_vault_dir)
    loaded = load_vault("myproject", "pass", vault_dir=tmp_vault_dir)
    assert loaded == env_vars


def test_vault_exists(tmp_vault_dir):
    assert not vault_exists("proj", vault_dir=tmp_vault_dir)
    save_vault("proj", {"X": "1"}, "pw", vault_dir=tmp_vault_dir)
    assert vault_exists("proj", vault_dir=tmp_vault_dir)


def test_list_vaults(tmp_vault_dir):
    save_vault("alpha", {}, "pw", vault_dir=tmp_vault_dir)
    save_vault("beta", {}, "pw", vault_dir=tmp_vault_dir)
    vaults = list_vaults(vault_dir=tmp_vault_dir)
    assert set(vaults) == {"alpha", "beta"}


def test_delete_vault(tmp_vault_dir):
    save_vault("todelete", {"K": "V"}, "pw", vault_dir=tmp_vault_dir)
    assert delete_vault("todelete", vault_dir=tmp_vault_dir) is True
    assert not vault_exists("todelete", vault_dir=tmp_vault_dir)
    assert delete_vault("todelete", vault_dir=tmp_vault_dir) is False


def test_load_missing_vault_raises(tmp_vault_dir):
    with pytest.raises(FileNotFoundError):
        load_vault("ghost", "pw", vault_dir=tmp_vault_dir)


def test_load_wrong_password_raises(tmp_vault_dir):
    save_vault("secure", {"K": "V"}, "right", vault_dir=tmp_vault_dir)
    with pytest.raises(ValueError):
        load_vault("secure", "wrong", vault_dir=tmp_vault_dir)
