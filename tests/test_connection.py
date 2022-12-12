import os
import pprint
from typing import Optional

from jira_access.jira_query_executor import JiraQueryExecutor


def test_connection():
    jira_api_token: Optional[str] = os.getenv("JIRA_API_TOKEN")
    jira_email: Optional[str] = os.getenv("JIRA_EMAIL")
    jira_base_url: Optional[str] = os.getenv("JIRA_BASE_URL")

    assert jira_api_token is not None, '"JIRA_API_TOKE" not set as an environment variable.'
    assert jira_email is not None, '"JIRA_EMAIl" not set as an environment variable.'
    assert jira_base_url is not None, '"JIRA_BASE_URL" not set as an environment variable'

    jira_query_exec = JiraQueryExecutor.from_mail_and_token(jira_email, jira_api_token, jira_base_url)

    jql_query = 'project = "TES" AND assignee = currentuser()'
    res = jira_query_exec.execute_jql_query(jql_query)
    pprint.pprint(res)
