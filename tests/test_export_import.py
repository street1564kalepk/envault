import os
import json
import pytest
from click.testing import CliRunner
from envault.cli import cli

PASSWORD = "testpassword"
PROJECT = "testproject"


@pytest.fixture
def isolated_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def initialized_vault(isolated_vault_dir, runner):
    runner.invoke(cli, ["init", "--project", PROJECT, "--password", PASSWORD])
    runner.invoke(cli, ["set", "--project", PROJECT, "--password", PASSWORD, "DB_HOST", "localhost"])
    runner.invoke(cli, ["set", "--project", PROJECT, "--password", PASSWORD, "DB_PORT", "5432"])
    runner.invoke(cli, ["set", "--project", PROJECT, "--password", PASSWORD, "SECRET", "mysecret"])
    return isolated_vault_dir


def test_export_dotenv_format(initialized_vault, runner):
    result = runner.invoke(cli, ["export", "--project", PROJECT, "--password", PASSWORD, "--format", "dotenv"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DB_PORT=5432" in result.output
    assert "SECRET=mysecret" in result.output


def test_export_shell_format(initialized_vault, runner):
    result = runner.invoke(cli, ["export", "--project", PROJECT, "--password", PASSWORD, "--format", "shell"])
    assert result.exit_code == 0
    assert "export DB_HOST=localhost" in result.output
    assert "export SECRET=mysecret" in result.output


def test_export_json_format(initialized_vault, runner):
    result = runner.invoke(cli, ["export", "--project", PROJECT, "--password", PASSWORD, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["DB_HOST"] == "localhost"
    assert data["SECRET"] == "mysecret"


def test_export_to_file(initialized_vault, runner):
    output_file = str(initialized_vault / "exported.env")
    result = runner.invoke(cli, ["export", "--project", PROJECT, "--password", PASSWORD, "--output", output_file])
    assert result.exit_code == 0
    assert os.path.exists(output_file)
    with open(output_file) as f:
        content = f.read()
    assert "DB_HOST=localhost" in content


def test_export_nonexistent_vault(isolated_vault_dir, runner):
    result = runner.invoke(cli, ["export", "--project", "ghost", "--password", PASSWORD])
    assert result.exit_code != 0


def test_import_dotenv_file(isolated_vault_dir, runner, tmp_path):
    runner.invoke(cli, ["init", "--project", PROJECT, "--password", PASSWORD])
    env_file = tmp_path / "sample.env"
    env_file.write_text("APP_ENV=production\nAPP_DEBUG=false\n# comment\n\nAPP_PORT=8080\n")
    result = runner.invoke(cli, ["import", str(env_file), "--project", PROJECT, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "3" in result.output or "Imported" in result.output

    get_result = runner.invoke(cli, ["get", "--project", PROJECT, "--password", PASSWORD, "APP_ENV"])
    assert "production" in get_result.output


def test_import_skips_existing_without_overwrite(initialized_vault, runner, tmp_path):
    env_file = tmp_path / "override.env"
    env_file.write_text("DB_HOST=newhost\nNEW_VAR=hello\n")
    result = runner.invoke(cli, ["import", str(env_file), "--project", PROJECT, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "Skipping" in result.output

    get_result = runner.invoke(cli, ["get", "--project", PROJECT, "--password", PASSWORD, "DB_HOST"])
    assert "localhost" in get_result.output


def test_import_overwrite_flag(initialized_vault, runner, tmp_path):
    env_file = tmp_path / "override.env"
    env_file.write_text("DB_HOST=newhost\n")
    runner.invoke(cli, ["import", str(env_file), "--project", PROJECT, "--password", PASSWORD, "--overwrite"])
    get_result = runner.invoke(cli, ["get", "--project", PROJECT, "--password", PASSWORD, "DB_HOST"])
    assert "newhost" in get_result.output


def test_import_missing_file(initialized_vault, runner):
    result = runner.invoke(cli, ["import", "nonexistent.env", "--project", PROJECT, "--password", PASSWORD])
    assert result.exit_code != 0
