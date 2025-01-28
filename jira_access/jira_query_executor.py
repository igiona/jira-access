# Author: Giona Imperatori
from __future__ import annotations

import sys

from requests.auth import AuthBase

from jira_access._jira_client import JiraClient
from jira_access._types import Json
from jira_access._types import JsonType
from jira_access.basic_auth import BasicAuth
from jira_access.bearer_auth import BearerAuth


class JiraQueryExecutor(JiraClient):
    """Simple class to execute Jira JQL queries via REST API using a Jira token as authentication method."""

    _MAX_RESULTS_PER_REQUESTS = 100

    def __init__(self, auth: AuthBase, jira_url: str):
        """Instantiate a executor bound to a authentication token.

        Args:
            auth: string containing the Jira access token
            jira_url: Jira server URL (e.g. "https://jira.myhost.com")
        """
        jira_url = self._strip_trailing_slash(jira_url)
        super().__init__(auth=auth, jira_api_url=f"{jira_url}/rest/api/latest")

    @classmethod
    def from_token(cls, access_token: str, jira_base_url: str):
        return cls(BearerAuth(access_token), jira_base_url)

    @classmethod
    def from_mail_and_token(cls, mail: str, token: str, jira_base_url: str):
        return cls(BasicAuth(mail, token), jira_base_url)

    def execute_jql_query(self, query: str, fields: List[str] = None, default_order: bool = True) -> list[JsonType]:
        """Execute a jql query

        Args:
            query: the JQL to be executed
            fields: list of the desired fields name as string. If None all fields will be returned
            default_order: if set, the results will be ordered by the updated field in descending order

        """

        def execute_http_search_request(query: str, start_at: int, max_results: int) -> Json | JsonType:
            # API description: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get # noqa, long url
            params = {
                "jql": query,
                "maxResults": str(max_results),
                "startAt": str(start_at),
            }
            if fields: 
                params["fields"] = ",".join(fields)
            return self._execute_http_get_request("/search", params=params)

        if default_order:
            query += " ORDER BY updated DESC"
        # print(query)

        total: int = sys.maxsize
        issues: list[Json | JsonType] = []
        while len(issues) < total:
            json_partial = execute_http_search_request(query, len(issues), self._MAX_RESULTS_PER_REQUESTS)

            assert isinstance(json_partial, dict), f"Received json_partial={json_partial} but should be 'dict'"
            assert isinstance(json_partial["issues"],
                              list), f"Received json_partial['issues']={json_partial['issues']} but should be 'list'"

            retrieved_issues_number = len(json_partial["issues"])

            assert isinstance(json_partial["total"],
                              int), f"Received json_partial['total']={json_partial['total']} but should be 'int'"

            total = int(json_partial["total"])

            if retrieved_issues_number != 0:
                issues.extend(json_partial["issues"])  # type: ignore # issues is always a list
            else:
                if total > 0:
                    print(f"WARNING: the last execution didn't return any result startAt={len(issues)} of {total}")
                break

        assert len(issues) == total, f"Number of results mismatch retrieved {len(issues)} of {total}"
        return issues

    def set_issue_field(self, issue_key: str, field: str, value: str, notify_users: bool = True) -> Json | JsonType:
        # API description: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-put # noqa, long url

        params: dict[str, str] = {"notifyUsers": str(notify_users)}
        body: Json = {"update": {field: [{"set": value}]}}
        return self._execute_http_put_request(data=body, api_action=f"/issue/{issue_key}", params=params)
