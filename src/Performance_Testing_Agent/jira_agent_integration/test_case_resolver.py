import re

from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

TEST_CASE_FIELD_ID = "customfield_10332"

# "PTC-005", and the spellings people type: "PTC 005", "ptc005".
_TEXT_TEST_CASE_ID = re.compile(r"\b(PTC|WTC)[-_ ]?(\d{3})\b", re.IGNORECASE)


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


def resolve_text_test_case(summary: str, description: str) -> dict | None:
    """Catalog test case an issue names in its text when no Test Case ID is selected.

    Naming the case ("Run PTC-005 using JMeter") then works like selecting it.
    Only one distinct ID may be named, and it must be an active catalog case.
    No ID, several IDs or an ID that is not in the catalog return None, so the
    issue is handled exactly as it was before.
    """
    found = {
        f"{prefix.upper()}-{digits}"
        for prefix, digits in _TEXT_TEST_CASE_ID.findall(
            f"{summary or ''}\n{description or ''}"
        )
    }
    if len(found) != 1:
        return None

    try:
        test_case = get_test_case(found.pop())
    except ValueError as exc:
        # An unknown ID is not a match; a broken catalog is still an error.
        if str(exc).startswith("Unknown test case ID"):
            return None
        raise

    if test_case.get("status", "active") != "active":
        return None

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