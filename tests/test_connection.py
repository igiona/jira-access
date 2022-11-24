import os
import pprint
from typing import Optional

from jira_access.jira_query_executor import JiraQueryExecutor

EMAIL: str = "ch.ungricht@scewo.ch"
JIRA_BASE_URL = "https://scewosw.atlassian.net/"


def test_connection():
    jira_api_token: Optional[str] = os.getenv("JIRA_API_TOKEN")

    assert jira_api_token is not None, '"JIRA_API_TOKE" not set as en environment variable.'

    jira_query_exec = JiraQueryExecutor.from_mail_and_token(EMAIL, jira_api_token, JIRA_BASE_URL)

    jql_query = 'project = "TES" AND assignee = currentuser()'
    res = jira_query_exec.execute_jql_query(jql_query)
    pprint.pprint(res)
