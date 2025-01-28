from __future__ import annotations

import json
from typing import IO, Mapping, Optional

import requests
from requests.auth import AuthBase

from jira_access._types import Json
from jira_access._types import JsonType


class JiraClient:
    _DEFAULT_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
    _REQUEST_TIMEOUT_SEC = 120

    def __init__(self, auth: Optional[AuthBase], jira_api_url: str):
        """Instantiate a jira client bound to an authentication token.

        Args:
            auth: Object containing the Jira credentials
            jira_api_url: Jira api server URL (e.g. "https://jira.myhost.com/rest/api/latest")
        """
        self._api_url: str = self._strip_trailing_slash(jira_api_url)
        self._auth: Optional[AuthBase] = auth

    def _execute_http_get_request(self,
                                  api_action: str,
                                  params: Optional[Mapping[str, str]] = None,
                                  headers: Optional[Mapping[str, str]] = None) -> JsonType:
        headers = headers or self._DEFAULT_HEADERS
        url = self._api_url + api_action
        r: requests.Response = requests.get(url,
                                            params=params,
                                            headers=headers,
                                            auth=self._auth,
                                            timeout=self._REQUEST_TIMEOUT_SEC)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing query '{params}'.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        return r.json()
    
    def _execute_http_get_streamed_request(self,
                                  api_action: str,
                                  params: Optional[Mapping[str, str]] = None,
                                  headers: Optional[Mapping[str, str]] = None,
                                  stream: bool = False) -> requests.Response:
        headers = headers or self._DEFAULT_HEADERS
        url = self._api_url + api_action
        r: requests.Response = requests.get(url,
                                            params=params,
                                            headers=headers,
                                            auth=self._auth,
                                            timeout=self._REQUEST_TIMEOUT_SEC,
                                            stream=True)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing query '{params}'.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        return r
    
    def _execute_http_post_requests_from_json_file(self,
                                                   json_file_path: str,
                                                   api_action: str,
                                                   params: Optional[Mapping[str, str]] = None,
                                                   headers: Optional[Mapping[str, str]] = None) -> JsonType:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self._execute_http_post_request(params=params, data=data, api_action=api_action, headers=headers)

    def _execute_http_post_request(self,
                                   data: Json | IO,
                                   api_action: str,
                                   params: Optional[Mapping[str, str]] = None,
                                   headers: Optional[Mapping[str, str]] = None) -> JsonType:
        headers = headers or self._DEFAULT_HEADERS
        payload = json.dumps(data) if isinstance(data, dict) else data
        url = self._api_url + api_action
        r: requests.Response = requests.post(url,
                                             params=params,
                                             data=payload,
                                             headers=headers,
                                             auth=self._auth,
                                             timeout=self._REQUEST_TIMEOUT_SEC)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing put request.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        return r.json()

    def _execute_http_put_requests_from_json_file(self,
                                                  json_file_path: str,
                                                  api_action: str,
                                                  params: Optional[Mapping[str, str]] = None,
                                                  headers: Optional[Mapping[str, str]] = None) -> JsonType:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self._execute_http_put_request(data=data, api_action=api_action, params=params, headers=headers)

    def _execute_http_put_request(self,
                                  data: Json | IO,
                                  api_action: str,
                                  params: Optional[Mapping[str, str]] = None,
                                  headers: Optional[Mapping[str, str]] = None) -> JsonType:
        headers = headers or self._DEFAULT_HEADERS
        payload = json.dumps(data) if isinstance(data, dict) else data
        url = self._api_url + api_action
        r: requests.Response = requests.put(url,
                                            params=params,
                                            data=payload,
                                            headers=headers,
                                            auth=self._auth,
                                            timeout=self._REQUEST_TIMEOUT_SEC)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing put request.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        return r.json()

    @staticmethod
    def _strip_trailing_slash(url: str) -> str:
        return url.rstrip("/")
