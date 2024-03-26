"""
Test fotoobo
"""

import re
from typing import List
from unittest.mock import MagicMock

import pytest

from _pytest.monkeypatch import MonkeyPatch
from _pytest.capture import CaptureFixture

from fotoobo import __version__
from fotoobo.exceptions import FotooboWarning
from fotoobo.exceptions.exceptions import FotooboException, FotooboError
from fotoobo.main import main


def test_version() -> None:
    """
    Testing the fotoobo version

    The RegEx used for testing the semantic version string is very simplified here but it is
    enough for fotoobo.
    Detailed information on RegEx testing semantic versions can be found here:
    https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
    """
    assert re.search(r"^[0-9]+\.[0-9]+\.[0-9]+", __version__)


def test_main() -> None:
    """
    Calling the main() function directly has the same effect as calling the cli app without any
    command line arguments. So main() will always exit with sys.exit(2).
    """
    try:
        main()
    except SystemExit as err:
        assert err.args[0] == 2


@pytest.mark.parametrize(
    "side_effect,expected_output,expected_exit_code",
    (
        pytest.param(
            FotooboWarning("Test Warning"),
            ["fotoobo finished with a warning", "Test Warning"],
            30,
            id="Warning",
        ),
        pytest.param(
            FotooboError("Test Error"),
            ["fotoobo finished with an error", "Test Error"],
            40,
            id="Error",
        ),
    ),
)
def test_main_with_errors(
    side_effect: FotooboException,
    expected_output: List[str],
    expected_exit_code: int,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """
    This tests the code that will be run, when a FotooboWarning or FotooboError reaches the main
    """

    monkeypatch.setattr("fotoobo.main.app", MagicMock(side_effect=side_effect))
    try:
        main()
    except SystemExit as err:
        assert err.args[0] == expected_exit_code

    out = capsys.readouterr()

    for entry in expected_output:
        assert entry in out.err
