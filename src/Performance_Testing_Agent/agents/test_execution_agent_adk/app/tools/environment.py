import os
import uuid
from datetime import datetime


ENVIRONMENT_DIR = "generated_data"


def prepare_environment(
    application: str,
    scenario: str,
    environment: str = "test",
    users: int = 1,
    requirements: str = "",
) -> dict:
    """
    Prepare the environment required for a performance test.

    Use this tool when the user asks to prepare a performance-testing
    environment, test accounts, virtual-user setup, credentials,
    or other execution prerequisites.

    Args:
        application: Application or system being tested.
        scenario: Performance-testing scenario.
        environment: Target environment such as test, QA, staging,
            or performance.
        users: Number of virtual users or test accounts required.
        requirements: Additional environment requirements.

    Returns:
        A dictionary containing the prepared environment information
        and configuration artifact.
    """

    if users < 1:
        return {
            "status": "error",
            "message": "Number of users must be greater than zero.",
        }

    os.makedirs(ENVIRONMENT_DIR, exist_ok=True)

    job_id = f"ENV-{uuid.uuid4().hex[:8]}"

    environment_config = {
        "environment_id": job_id,
        "application": application,
        "scenario": scenario,
        "environment": environment,
        "users": users,
        "requirements": requirements,
        "prepared_at": datetime.utcnow().isoformat(),
        "status": "prepared",
    }

    file_name = f"environment_{job_id}.json"

    file_path = os.path.join(
        ENVIRONMENT_DIR,
        file_name,
    )

    import json

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as environment_file:
        json.dump(
            environment_config,
            environment_file,
            indent=2,
        )

    return {
        "status": "success",
        "message": "Performance-testing environment prepared successfully.",
        "environment_id": job_id,
        "application": application,
        "scenario": scenario,
        "environment": environment,
        "users": users,
        "configuration_file": file_path,
    }