
# Author: Giona Imperatori
#
# Simple class to execute Jira JQL queries via REST API using a Jira token as authentication method.
# It requires the "requests" module to be installed

import json
import sys
import requests
from BasicAuth import BasicAuth
from BearerAuth import BearerAuth

# accessToken : string containing the Jira access token
# jiraBaseUrl : Jira server URL (e.g. "https://jira.myhost.com")
class JiraQueryExecutor:
    _maxResultsPerRequest = 100

    def __init__(self, auth, jiraBaseUrl):
        self._apiBaseUrl = f"{jiraBaseUrl}/rest/api/latest"
        self._auth = auth

    @classmethod
    def from_token(cls, accessToken, jiraBaseUrl):
        return cls(BearerAuth(accessToken), jiraBaseUrl)

    @classmethod
    def from_mail_and_token(cls, mail, token, jiraBaseUrl):
        return cls(BasicAuth(mail, token), jiraBaseUrl)
    
    def _execute_http_get_request(self, params, apiAction):       
        url = self._apiBaseUrl + apiAction
        headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }
        r = requests.get(url, params=params, headers=headers, auth=self._auth, timeout=120)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing query '{params}'.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        return r.json()

    def _execute_http_put_request(self, params, body, apiAction):       
        url = self._apiBaseUrl + apiAction
        headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }
        r = requests.put(url, params=params, data=json.dumps(body), headers=headers, auth=self._auth, timeout=120)

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing put request.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()

    # query: the JQL to be executed
    # defaultOrder: if set, the results will be ordered by the updated field in descending order
    def execute_jql_query(self, query, defaultOrder = True):
        def execute_http_search_request(query, startAt, maxResults):
            #API description: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
            params = {
                'jql': query,
            }
            params['maxResults'] = str(maxResults)
            params['startAt'] = str(startAt)
            return self._execute_http_get_request(params, "/search")
        
        if defaultOrder:
            query += " ORDER BY updated DESC"
        #print(query)
        
        total = sys.maxsize
        issues = []
        while len(issues) < total:
            json_partial = execute_http_search_request(query, len(issues), self._maxResultsPerRequest)
            retrievedIssuesNumber = len(json_partial["issues"])
            total = int(json_partial["total"])

            if retrievedIssuesNumber != 0:
                issues.extend(json_partial["issues"])
            else:
                if total > 0:
                    print(f"WARNING: the last execution didn't return any result startAt={len(issues)} of {total}")
                break

        assert len(issues) == total, f'Number of results mismatch retrieved {len(issues)} of {total}'
        return issues

    def set_issue_field(self, issueKey, field, value, notifyUsers = True):
        #API description: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-put

        params = {
            'notifyUsers' : str(notifyUsers)
        }
        body = {
            "update": {
                field: [
                    {
                        "set": value
                    }
                ]
            }
        }
        return self._execute_http_put_request(params, body, f"/issue/{issueKey}")
