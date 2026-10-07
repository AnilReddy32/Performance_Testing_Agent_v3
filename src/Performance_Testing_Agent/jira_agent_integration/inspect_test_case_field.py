import json

from Performance_Testing_Agent.jira_agent_integration.app.jira_client import (
    find_test_case_fields,
    inspect_field_contexts,
)


def main():
    fields = find_test_case_fields()

    if not fields:
        print("No accessible field named 'Test Case ID' was found.")
        return

    for field in fields:
        print("\n=== MATCHING FIELD ===")
        print(json.dumps(
            {
                "id": field.get("id"),
                "name": field.get("name"),
                "schema": field.get("schema"),
                "scope": field.get("scope"),
            },
            indent=2,
        ))

        print("\n=== CONTEXT API RESPONSE ===")
        result = inspect_field_contexts(field["id"])
        print("HTTP status:", result["status_code"])
        print(result["body"])


if __name__ == "__main__":
    main()