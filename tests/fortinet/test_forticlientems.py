# type: ignore
"""
Test the FortiClient EMS class
"""
from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import APIError, FotooboWarning
from fotoobo.fortinet.forticlientems import FortiClientEMS
from tests.helper import ResponseMock


class TestFortiClientEMS:
    """Test the FortiClientEMS class"""

    @staticmethod
    def test_login_without_cookie(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with no session cookie given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={"result": {"retval": 1, "message": "Login successful."}},
                    status=200,
                )
            ),
        )
        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", ssl_verify=False)
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200
        assert ems.session.headers["Referer"] == "https://ems_dummy"
        assert ems.session.headers["X-CSRFToken"] == "dummy_csrf_token"

    @staticmethod
    def test_login_with_valid_cookie(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with valid session cookie path given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": {"retval": 1, "message": "Login successful."}}, status=200
                )
            ),
        )
        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", "tests/data/", ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200
        assert ems.session.headers["Referer"] == "https://ems_dummy"
        assert ems.session.headers["X-CSRFToken"] == "dummy_csrf_token_from_cache\n"

    @staticmethod
    def test_login_with_invalid_cookie(monkeypatch: MonkeyPatch, temp_dir: Path) -> None:
        """Test the login to a FortiClient EMS with no session cookie given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "result": {
                            "retval": -4,
                            "message": "Session has expired or does not exist.",
                        },
                    },
                    status=401,
                )
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status=200,
                ),
            ),
        )
        source = Path("tests/data/ems_dummy.cookie")
        destination = Path(temp_dir / "ems_dummy.cookie")
        destination.write_bytes(source.read_bytes())
        source = Path("tests/data/ems_dummy.csrf")
        destination = Path(temp_dir / "ems_dummy.csrf")
        destination.write_bytes(source.read_bytes())
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://host:443/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_login_with_invalid_cookie_path(temp_dir: Path, monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with an invalid cookie path"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status=200,
                )
            ),
        )
        ems = FortiClientEMS("host_1", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://host_1:443/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_login_with_csrf_token_not_found(temp_dir: Path, monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS when the csrf token was not found in the headers"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken_missing=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status=200,
                )
            ),
        )
        ems = FortiClientEMS("host_2", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://host_2:443/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_logout_with_valid_session(monkeypatch: MonkeyPatch) -> None:
        """Test the logout from a FortiClient EMS with a valid session"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={}, status=200)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)
        response = ems.logout()
        assert response == 200

    @staticmethod
    def test_logout_with_invalid_session(monkeypatch: MonkeyPatch) -> None:
        """Test the logout from a FortiClient EMS with an invalid session"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={}, status=401)),
        )
        with pytest.raises(APIError) as err:
            FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False).logout()
        assert "HTTP/401 Not Authorized" in str(err.value)

    @staticmethod
    def test_get_version_ok(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with a valid get response"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={"data": {"System": {"VERSION": "1.2.3"}}},
                    status=200,
                )
            ),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass")
        response = ems.get_version()
        requests.Session.get.assert_called_with(
            "https://host:443/api/v1/system/consts/get?system_update_time=1",
            headers=ANY,
            json=None,
            params=None,
            timeout=3,
            verify=True,
        )
        assert response == "1.2.3"

    @staticmethod
    def test_get_version_invalid(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with an invalid get response (invalid data, no version)"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={"data": {"System": {}}}, status=200)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)
        with pytest.raises(FotooboWarning) as err:
            ems.get_version()
        assert "Did not find any FortiClient EMS version number in response" in str(err.value)
        requests.Session.get.assert_called_with(
            "https://host:443/api/v1/system/consts/get?system_update_time=1",
            headers=ANY,
            json=None,
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_get_version_api_error(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with an APIError exception"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
            MagicMock(side_effect=APIError(999)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)
        with pytest.raises(FotooboWarning, match=r"host returned: unknown"):
            ems.get_version()
