from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

TEST_CASE_FIELD_ID = "customfield_10332"


def resolve_issue_test_case(issue: dict) -> dict | None:
    """Return the catalog test case, or None if no Test Case ID is selected."""
    fields = issue.get("fields") or {}
    selected_option = fields.get(TEST_CASE_FIELD_ID)

    # No Test Case ID selected -> caller falls back to attachment or
    # summary/description.
    if not isinstance(selected_option, dict):
        return None

    test_case_id = selected_option.get("value")

    if not isinstance(test_case_id, str) or not test_case_id.strip():
        return None

    # Raises ValueError if the ID does not exist in the catalog.
    test_case = get_test_case(test_case_id)

    # Your current entries have no status, so they default to active.
    if test_case.get("status", "active") != "active":
        raise ValueError(f"Test case {test_case_id} is not active.")

    return test_case


def build_test_case_prompt(test_case: dict) -> str:
    """Prompt stored in the test case, or one built from its fields."""
    prompt = test_case.get("prompt")

    if isinstance(prompt, str) and prompt.strip():
        return prompt.strip()

    return (
        f"Run the performance test '{test_case.get('name', test_case['test_case_id'])}' "
        f"(test case {test_case['test_case_id']}) on "
        f"{test_case.get('api')} {test_case.get('method')} "
        f"{test_case.get('endpoint')} with {test_case.get('virtual_users')} "
        f"virtual users for {test_case.get('duration_seconds')} seconds, "
        f"ramp-up {test_case.get('ramp_up_seconds')} seconds. "
        f"Expected response time: {test_case.get('expected_response_time_ms')} ms, "
        f"expected status code: {test_case.get('expected_status_code')}. "
        "Analyze the results and report them."
    )