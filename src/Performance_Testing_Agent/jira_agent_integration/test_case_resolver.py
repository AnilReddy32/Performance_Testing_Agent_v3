from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

TEST_CASE_FIELD_ID = "customfield_10332"


def resolve_issue_test_case(issue: dict) -> dict:
    fields = issue.get("fields") or {}
    selected_option = fields.get(TEST_CASE_FIELD_ID)

    if not isinstance(selected_option, dict):
        raise ValueError(
            "Test Case ID is missing or was not included "
            "in the Jira API response."
        )

    test_case_id = selected_option.get("value")

    if not isinstance(test_case_id, str) or not test_case_id.strip():
        raise ValueError("Test Case ID is empty.")

    # Raises ValueError if the ID does not exist in the catalog.
    test_case = get_test_case(test_case_id)

    # Your current entries have no status, so they default to active.
    if test_case.get("status", "active") != "active":
        raise ValueError(f"Test case {test_case_id} is not active.")

    return test_case