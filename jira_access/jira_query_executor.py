# Author: Giona Imperatori
from __future__ import annotations

import json
import sys
from typing import Dict, List, Union

import requests
from requests.auth import AuthBase

from jira_access.basic_auth import BasicAuth
from jira_access.bearer_auth import BearerAuth

Json = Dict[str, Union[None, int, str, bool, List["Json"], "Json"]]


class JiraQueryExecutor:
    """Simple class to execute Jira JQL queries via REST API using a Jira token as authentication method."""

    _MAX_RESULTS_PER_REQUESTS = 100

    def __init__(self, auth: AuthBase, jira_base_url: str):
        """Instantiate a executor bound to a authentication token

        Args:
            auth: string containing the Jira access token
            jira_base_url: Jira server URL (e.g. "https://jira.myhost.com")
        """
        self._api_base_url: str = f"{jira_base_url}/rest/api/latest"
        self._auth: AuthBase = auth

    @classmethod
    def from_token(cls, access_token: str, jira_base_url: str) -> JiraQueryExecutor:
        return cls(BearerAuth(access_token), jira_base_url)

    @classmethod
    def from_mail_and_token(cls, mail: str, token: str, jira_base_url: str) -> JiraQueryExecutor:
        return cls(BasicAuth(mail, token), jira_base_url)

    def _execute_http_get_request(self, params: dict[str, str], api_action: str) -> Json:
        url = self._api_base_url + api_action
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        r: requests.Response = requests.get(url, params=params, headers=headers, auth=self._auth, timeout=120)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing query '{params}'.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        return r.json()

    def _execute_http_put_request(self, params: dict[str, str], body: Json, api_action: str) -> None:
        url = self._api_base_url + api_action
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        r: requests.Response = requests.put(url,
                                            params=params,
                                            data=json.dumps(body),
                                            headers=headers,
                                            auth=self._auth,
                                            timeout=120)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing put request.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()

    def execute_jql_query(self, query: str, default_order: bool = True) -> list[Json]:
        """Execute a jql query

        Args:
            query: the JQL to be executed
            default_order: if set, the results will be ordered by the updated field in descending order

        """

        def execute_http_search_request(query: str, start_at: int, max_results: int) -> Json:
            # API description: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get # noqa, long url
            params = {
                "jql": query,
                "maxResults": str(max_results),
                "startAt": str(start_at),
            }
            return self._execute_http_get_request(params, "/search")

        if default_order:
            query += " ORDER BY updated DESC"
        # print(query)

        total: int = sys.maxsize
        issues: list[Json] = []
        while len(issues) < total:
            json_partial: Json = execute_http_search_request(query, len(issues), self._MAX_RESULTS_PER_REQUESTS)
            retrieved_issues_number = len(json_partial["issues"])  # type: ignore # issues is always a list
            total = int(json_partial["total"])  # type: ignore # total is always an int

            if retrieved_issues_number != 0:
                issues.extend(json_partial["issues"])  # type: ignore # issues is always a list
            else:
                if total > 0:
                    print(f"WARNING: the last execution didn't return any result startAt={len(issues)} of {total}")
                break

        assert len(issues) == total, f"Number of results mismatch retrieved {len(issues)} of {total}"
        return issues

    def set_issue_field(self, issue_key: str, field: str, value: str, notify_users: bool = True) -> None:
        # API description: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-put # noqa, long url

        params: dict[str, str] = {"notifyUsers": str(notify_users)}
        body: Json = {"update": {field: [{"set": value}]}}
        return self._execute_http_put_request(params, body, f"/issue/{issue_key}")
