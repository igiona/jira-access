from jira_access.xray import Xray


def test_xray_authentication(xray_auth_file):
    xray = Xray.from_id_and_secret_file(xray_auth_file)
    xray.authenticate()


def test_xray_create_new_test_execution(xray_auth_file):
    xray = Xray.from_id_and_secret_file(xray_auth_file)
    xray.import_execution_from_file("./tests/data/create_new_test_execution.json")
