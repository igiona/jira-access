
# Author: Giona Imperatori
#
# Simple class to execute Jira JQL queries via REST API using a Jira token as authentication method.
# It requires the "requests" module to be installed

import requests
from BasicAuth import BasicAuth
from BearerAuth import BearerAuth

# accessToken : string containing the Jira access token
# jiraBaseUrl : Jira server URL (e.g. "https://jira.myhost.com")
class JiraQueryExecutor:

    def __init__(self, auth, jiraBaseUrl):
        self._apiBaseUrl = f"{jiraBaseUrl}/rest/api/latest"
        self._auth = auth

    @classmethod
    def from_token(cls, accessToken, jiraBaseUrl):
        return cls(BearerAuth(accessToken), jiraBaseUrl)

    @classmethod
    def from_mail_and_token(cls, mail, token, jiraBaseUrl):
        return cls(BasicAuth(mail, token), jiraBaseUrl)
    
    # query: the JQL to be executed
    # defaultOrder: if set, the results will be ordered by the updated field in descending order
    # maxResults: if set, the integer value is used to limit the number of results of the query
    def execute_jql_query(self, query, defaultOrder = True, maxResults = None):
        def execute_http_request(query, startAt, maxResults):
            params = {
                'jql': query,
            }

            if maxResults != None:
                params['maxResults'] = str(maxResults)
            if startAt == None:
                startAt = 0
            
            params['startAt'] = str(startAt)
            
            url = self._apiBaseUrl + "/search"
            #print(f"GET: {url} with {params}")
            #headers = { 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Atlassian-Token': 'nocheck' }
            headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }
            #auth = HTTPBasicAuth(user, passwd)
            r = requests.get(url, params=params, headers=headers, auth=self._auth, timeout=120)
            #print(f"GET: {r.url}")

            if not r.ok:
                if r.status_code == 400:
                    raise Exception(f"Error executing query '{query}'.\nError message: {r.json()}\nURL: {r.url}")
                r.raise_for_status()
            return r.json()
        
        if defaultOrder:
            query += " ORDER BY updated DESC"
        #print(query)
        json = execute_http_request(query, 0, maxResults)
        assert len(json["issues"]) == int(json["total"]), f'Number of results mismatch: {len(json["issues"])} vs {json["total"]}'
        
        return json