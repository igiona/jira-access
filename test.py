import os
import pprint
from typing import Optional

from JiraQueryExecutor import JiraQueryExecutor

EMAIL: str = "ch.ungricht@scewo.ch"
JIRA_BASE_URL = "https://scewosw.atlassian.net/"


def main():
    jira_api_token: Optional[str] = os.getenv("JIRA_API_TOKEN")

    if jira_api_token is None:
        raise ValueError('"JIRA_API_TOKE" not set as en environment variable.')

    jira_query_exec = JiraQueryExecutor.from_mail_and_token(
        EMAIL, jira_api_token, JIRA_BASE_URL)

    jql_query = 'project = "TES" AND assignee = currentuser()'
    res = jira_query_exec.execute_jql_query(jql_query)
    pprint.pprint(res)


if __name__ == "__main__":
    main()
