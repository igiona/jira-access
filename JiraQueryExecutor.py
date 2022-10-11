
# Author: Giona Imperatori
#
# Simple class to execute Jira JQL queries via REST API using a Jira token as authentication method.
# It requires the "requests" module to be installed

import requests
from BearerAuth import BearerAuth

# accessToken : string containing the Jira access token
# jiraBaseUrl : Jira server URL (e.g. "https://jira.myhost.com")
class JiraQueryExecutor:
    def __init__(self, accessToken, jiraBaseUrl):
        self._token = accessToken
        self._apiBaseUrl = f"{jiraBaseUrl}/rest/api/latest"
    
    # query: the JQL to be executed
    # defaultOrder: if set, the results will be ordered by the updated field in descending order
    # maxResults: if set, the integer value is used to limit the number of results of the query
    def ExecuteJqlQuery(self, query, defaultOrder = True, maxResults = None): 
        if defaultOrder:
            query += " ORDER BY updated DESC"
        #print(query)
        params = {
            'jql': query,
        }

        if maxResults != None:
            params['maxResults'] = str(maxResults)
        
        url = self._apiBaseUrl + "/search"
        #print(f"GET: {url} with {params}")
        #headers = { 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Atlassian-Token': 'nocheck' }
        headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }
        #auth = HTTPBasicAuth(user, passwd)
        auth = BearerAuth(self._token)
        r = requests.get(url, params=params, headers=headers, auth=auth, timeout=120)
        #print(f"GET: {r.url}")

        if not r.ok:
            if r.status_code == 400:
                raise Exception(f"Error executing query '{query}'.\nError message: {r.json()}\nURL: {r.url}")
            r.raise_for_status()
        json = r.json()
        assert len(json["issues"]) == int(json["total"]), f'Number of results mismatch: {len(json["issues"])} vs {json["total"]}'
        
        return json