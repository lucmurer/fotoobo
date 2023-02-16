"""
Testing the cli fgt check
"""
from unittest.mock import MagicMock, patch

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.helpers.cli import parse_help_output
from tests.helper import ResponseMock

runner = CliRunner()


def test_cli_app_fgt_check_help() -> None:
    """Test cli help for fgt check"""
    result = runner.invoke(app, ["fgt", "check", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"hamaster"}


def test_cli_app_fgt_check_hamaster_help() -> None:
    """Test cli help for fgt check hamaster"""
    result = runner.invoke(app, ["fgt", "check", "hamaster", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "--smtp"}
    assert not commands


@patch(
    "fotoobo.fortinet.fortinet.requests.Session.get",
    MagicMock(return_value=ResponseMock(json={"version": "v1.1.1"}, status=200)),
)
def test_cli_app_fgt_get_version() -> None:
    """Test cli options and commands for fgt get version"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "test_fgt_1"])
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 1


def test_cli_app_fgt_get_version_dummy() -> None:
    """Test cli options and commands for fgt get version with unknown host"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "dummy_fgt"])
    assert result.exit_code == 1


@patch(
    "fotoobo.fortinet.fortinet.requests.Session.get",
    MagicMock(return_value=ResponseMock(json={"version": "v1.1.1"}, status=200)),
)
def test_cli_app_fgt_get_version_all() -> None:
    """Test cli options and commands for fgt get version without specifying a host"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version"])
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 2


def test_cli_app_fgt_get_version_401(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fgt get version with error 401"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(
            return_value=ResponseMock(json={"dummy": "dummy"}, status=401),
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "test_fgt_1"])
    assert "HTTP/401 Not Authorized" in result.stdout
    assert result.exit_code == 0