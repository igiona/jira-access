from __future__ import annotations

from enum import Enum
from functools import wraps
import json
from typing import Optional

from jira_access._jira_client import JiraClient
from jira_access._types import Json
from jira_access._types import JsonType
from jira_access.bearer_auth import BearerAuth


class XrayApiVersion(Enum):
    V1 = "v1"
    V2 = "v2"


DEFAULT_API_VERSION = XrayApiVersion.V2


def _authenticated(fun):
    """A decorator used by the Xray class for lazy authentication."""

    @wraps(fun)
    def authenticate_before_running(self, *args, **kwargs):
        if self._auth is None:  # pylint: disable=protected-access, only used for methods in class
            self.authenticate()
        fun(self, *args, **kwargs)

    return authenticate_before_running


class Xray(JiraClient):
    _XRAY_API_BASE_URL = "https://xray.cloud.getxray.app"

    def __init__(self, auth: Optional[BearerAuth] = None, api_version: XrayApiVersion = DEFAULT_API_VERSION):
        self._client_id: Optional[str] = None
        self._client_secret: Optional[str] = None
        super().__init__(auth, f"{self._XRAY_API_BASE_URL}/api/{api_version.value}")

    @classmethod
    def from_id_and_secret(cls, client_id: str, client_secret: str, api_version: XrayApiVersion = DEFAULT_API_VERSION):
        self = cls(auth=None, api_version=api_version)
        self._client_id = client_id
        self._client_secret = client_secret
        return self

    @classmethod
    def from_id_and_secret_file(cls, json_file_path: str, api_version: XrayApiVersion = DEFAULT_API_VERSION):
        with open(json_file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        return cls.from_id_and_secret(**content, api_version=api_version)

    def authenticate(self) -> None:
        data: Json = {"client_id": self._client_id, "client_secret": self._client_secret}
        token = self._execute_http_post_request(data=data, api_action="/authenticate")
        assert isinstance(token, str), f"Received token={token} but should be 'str'"
        self._auth = BearerAuth(token)

    @_authenticated
    def import_execution_from_file(self, json_file_path: str) -> JsonType:
        return self._execute_http_post_requests_from_json_file(json_file_path=json_file_path,
                                                               api_action="/import/execution")
