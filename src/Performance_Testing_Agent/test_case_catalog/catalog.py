import json
from pathlib import Path
from typing import Any

from Performance_Testing_Agent.execution_context import (
    workload_profile_from_test_case,
)


CATALOG_DIRECTORY = Path(__file__).resolve().parent

CATALOG_FILES = (
    CATALOG_DIRECTORY / "performance_tests.json",
    CATALOG_DIRECTORY / "workflow_tests.json",
)


def load_test_cases() -> list[dict[str, Any]]:
    """Load both catalogs and reject duplicate or missing test-case IDs."""

    all_test_cases: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}

    for catalog_path in CATALOG_FILES:
        with catalog_path.open("r", encoding="utf-8") as file:
            test_cases = json.load(file)

        if not isinstance(test_cases, list):
            raise ValueError(
                f"{catalog_path.name} must contain a JSON array."
            )

        for index, test_case in enumerate(test_cases):
            if not isinstance(test_case, dict):
                raise ValueError(
                    f"{catalog_path.name}: entry {index} must be an object."
                )

            test_case_id = test_case.get("test_case_id")

            if (
                not isinstance(test_case_id, str)
                or not test_case_id.strip()
            ):
                raise ValueError(
                    f"{catalog_path.name}: entry {index} requires "
                    "a non-empty test_case_id."
                )

            if test_case_id in seen_ids:
                raise ValueError(
                    f"Duplicate test_case_id: {test_case_id}. "
                    f"Found in {seen_ids[test_case_id]} "
                    f"and {catalog_path.name}."
                )

            execution_mode = str(
                test_case.get("execution_mode", "SIMULATED")
            ).strip().upper()
            if execution_mode not in {"REAL", "SIMULATED"}:
                raise ValueError(
                    f"{catalog_path.name}: {test_case_id} has invalid "
                    "execution_mode; expected REAL or SIMULATED."
                )

            test_case["execution_mode"] = execution_mode
            test_case["workload_profile"] = (
                workload_profile_from_test_case(test_case).model_dump(
                    mode="json"
                )
            )

            seen_ids[test_case_id] = catalog_path.name
            all_test_cases.append(test_case)

    return all_test_cases


def get_test_case(test_case_id: str) -> dict[str, Any]:
    """Find a test case in either catalog."""

    for test_case in load_test_cases():
        if test_case["test_case_id"] == test_case_id:
            return test_case

    raise ValueError(f"Unknown test case ID: {test_case_id}")