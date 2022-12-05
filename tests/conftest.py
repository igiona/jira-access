import os

import pytest

XRAY_AUTH_FILE = "./tests/data/cloud_auth.json"
XRAY_AUTH_JSON_TEMPLATE = """{
  "client_id": <id-string>,
  "client_secret": <secret-string>
}
"""


@pytest.fixture()
def xray_auth_file() -> str:
    if not os.path.isfile(XRAY_AUTH_FILE):
        with open(XRAY_AUTH_FILE, "w", encoding="utf-8") as f:
            f.write(XRAY_AUTH_JSON_TEMPLATE)
            raise AssertionError(f"{XRAY_AUTH_FILE} not found. Template generated. Please fill in id and secret. "
                                 f"To generate an API key please visit the Xray tab in your Jira settings.")
    else:
        return XRAY_AUTH_FILE
