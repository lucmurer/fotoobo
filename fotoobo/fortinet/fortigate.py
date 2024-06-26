"""
FortiGate Class
"""
import logging
from typing import Any, Dict, Optional

import requests

from fotoobo.exceptions import APIError, FotooboWarning

from .fortinet import Fortinet

log = logging.getLogger("fotoobo")


class FortiGate(Fortinet):
    """
    Represents one FortiGate (digital twin)
    """

    def __init__(
        self,
        hostname: str = "",
        token: str = "",
        **kwargs: Dict[str, str],
    ) -> None:
        """
        Set some initial parameters.

        Args:
            hostname: The hostname of the FortiGate to connect to
            token:    API access token from the FortiGate
            **kwargs: See Fortinet class for available arguments
        """
        if not hostname:
            raise FotooboWarning("No hostname specified")

        super().__init__(hostname=hostname, **kwargs)
        self.api_url = f"https://{self.hostname}:{self.https_port}/api/v2"
        self.token = token
        self.type = "fortigate"

    def api(  # pylint: disable=too-many-arguments
        self,
        method: str,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> requests.models.Response:
        """
        API request to a FortiGate device.
        It uses the super.api method but it has to enrich the payload in post requests with the
        needed session key.

        Args:
            method:  Request method from [get, post]
            url:     Rest API URL to request data from
            params:  Dictionary with parameters (if needed)
            payload: JSON body for post requests (if needed)
            timeout: The requests read timeout

        Returns:
            Response from the request
        """
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return super().api(
            method, url, payload=payload, params=params, timeout=timeout, headers=headers
        )

    def backup(self, timeout: int = 10) -> str:
        """
        Get the configuration backup from a FortiGate.

        Args:
            timeout: Timeout in sec to wait for the response

        Returns:
            Configuration backup as text
        """
        data = self.api(
            "get", "monitor/system/config/backup", params={"scope": "global"}, timeout=timeout
        )
        return data.text

    def get_version(self) -> str:
        """
        Get FortiGate version

        Returns:
            FortiGate version
        """
        fgt_version: str = ""

        try:
            response = self.api("get", "monitor/system/status")

        except APIError as err:
            log.warning("'%s' returned: '%s'", self.hostname, err.message)
            raise FotooboWarning(f"{self.hostname} returned: {err.message}") from err

        fgt_version = response.json().get("version", "unknown")
        return fgt_version
