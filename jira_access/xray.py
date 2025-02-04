"""Module to interact with the Xray API."""

from __future__ import annotations

import json
from enum import Enum
from functools import wraps
from typing import TYPE_CHECKING, Optional

from jira_access._jira_client import JiraClient
from jira_access.bearer_auth import BearerAuth

if TYPE_CHECKING:
    from jira_access._types import Json, JsonType


class XrayApiVersion(Enum):
    """Enum to define the Xray API version."""

    V1 = "v1"
    V2 = "v2"


DEFAULT_API_VERSION = XrayApiVersion.V2


def _authenticated(fun):
    """A decorator used by the Xray class for lazy authentication."""  # noqa: DOC201

    @wraps(fun)
    def authenticate_before_running(self, *args, **kwargs):
        if self._auth is None:
            self.authenticate()
        fun(self, *args, **kwargs)

    return authenticate_before_running


class Xray(JiraClient):
    """Class to interact with the Xray API."""

    _XRAY_API_BASE_URL = "https://xray.cloud.getxray.app"

    def __init__(self, auth: Optional[BearerAuth] = None, api_version: XrayApiVersion = DEFAULT_API_VERSION):
        """Instantiate a Xray client bound to an authentication token.

        Args:
            auth: Authenticater containing the Xray credentials
            api_version: Xray API version to
        """
        self._client_id: Optional[str] = None
        self._client_secret: Optional[str] = None
        super().__init__(auth, f"{self._XRAY_API_BASE_URL}/api/{api_version.value}")

    @classmethod
    def from_id_and_secret(cls, client_id: str, client_secret: str, api_version: XrayApiVersion = DEFAULT_API_VERSION):
        """Instantiate a Xray client bound to a client_id and client_secret.

        Args:
            client_id: the client_id of the user
            client_secret: the client_secret of the user
            api_version: the Xray API version

        Returns:
            a new instance of Xray
        """
        self = cls(auth=None, api_version=api_version)
        self._client_id = client_id
        self._client_secret = client_secret
        return self

    @classmethod
    def from_id_and_secret_file(cls, json_file_path: str, api_version: XrayApiVersion = DEFAULT_API_VERSION):
        """Instantiate a Xray client using a json file containing the client_id and client_secret.

        Args:
            json_file_path: the path to the json file containing the client_id and client_secret
            api_version: the Xray API version

        Returns:
            a new instance of Xray
        """
        with open(json_file_path, encoding="utf-8") as f:
            content = json.load(f)
        return cls.from_id_and_secret(**content, api_version=api_version)

    def authenticate(self) -> None:
        """Authenticate the client."""
        data: Json = {"client_id": self._client_id, "client_secret": self._client_secret}
        token = self._execute_http_post_request(data=data, api_action="/authenticate")
        assert isinstance(token, str), f"Received token={token} but should be 'str'"
        self._auth = BearerAuth(token)

    @_authenticated
    def import_execution_from_file(self, json_file_path: str) -> JsonType:
        """Import an Xray execution from a json file.

        Args:
            json_file_path: the path to the json file containing the execution

        Returns:
            the response from the API
        """
        return self._execute_http_post_requests_from_json_file(
            json_file_path=json_file_path, api_action="/import/execution"
        )
