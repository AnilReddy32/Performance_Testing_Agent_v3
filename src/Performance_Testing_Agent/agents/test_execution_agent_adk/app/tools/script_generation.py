import os
import re
from pathlib import Path

from app.tools.artifact_generator import ArtifactGenerator
from app.tools.k6_template import build_real_k6_script
from Performance_Testing_Agent.execution_context import (
    resolve_artifact_directory,
    workload_profile_from_test_case,
)


GENERATED_SCRIPTS_DIR = str(
    Path(__file__).resolve().parents[5] / "generated_scripts"
)


def generate_script(
    tool,
    application,
    scenario,
    api_name,
    *,
    execution_mode="SIMULATED",
    workload_profile=None,
    job_id=None,
    artifact_directory=None,
    test_case_id=None,
    test_case_name=None,
):

    tool = tool.lower().strip()
    execution_mode = execution_mode.strip().upper()

    extensions = {
        "jmeter": ".jmx",
        "k6": ".js",
        "gatling": ".scala",
    }

    if tool not in extensions:
        return {
            "status": "error",
            "message": (
                f"Unsupported performance-testing tool: {tool}. "
                "Supported tools are JMeter, k6, and Gatling."
            ),
        }

    if execution_mode == "REAL":
        if tool != "k6":
            return {
                "status": "error",
                "message": (
                    "Deterministic REAL script generation is currently "
                    "available only for k6."
                ),
                "tool": tool,
                "execution_mode": execution_mode,
            }
        if not isinstance(workload_profile, dict):
            return {
                "status": "error",
                "message": (
                    "REAL k6 script generation requires the trusted "
                    "workload profile from session state."
                ),
                "tool": tool,
                "execution_mode": execution_mode,
            }
        if not job_id:
            return {
                "status": "error",
                "message": "REAL k6 script generation requires a job_id.",
                "tool": tool,
                "execution_mode": execution_mode,
            }

        try:
            profile = workload_profile_from_test_case(
                {"workload_profile": workload_profile}
            )
            expected_directory = resolve_artifact_directory(job_id)
            if artifact_directory is None:
                raise ValueError("REAL k6 generation requires a job artifact directory.")
            job_directory = Path(artifact_directory).expanduser().resolve()
            if job_directory != expected_directory:
                raise ValueError(
                    "The supplied artifact directory does not match this job."
                )
            script_content = build_real_k6_script(
                profile.model_dump(mode="json"),
                test_case_id=test_case_id,
            )
        except ValueError as exc:
            return {
                "status": "error",
                "message": str(exc),
                "tool": tool,
                "execution_mode": execution_mode,
            }

        job_directory.mkdir(parents=True, exist_ok=True)
        if isinstance(test_case_name, str) and test_case_name.strip():
            title = test_case_name
        else:
            title_parts = [
                value.strip()
                for value in (scenario, api_name)
                if isinstance(value, str)
                and value.strip()
                and value.strip().lower() not in {"unknown", "performance test"}
            ]
            title = " ".join(dict.fromkeys(title_parts)) or "performance_test"
        safe_title = _sanitize_filename(title) or "performance_test"
        safe_test_case_id = _sanitize_filename(test_case_id or "")
        file_parts = ["k6"]
        if safe_test_case_id:
            file_parts.append(safe_test_case_id)
        file_parts.append(safe_title)
        script_path = job_directory / f"{'_'.join(file_parts)}.js"
        script_path.write_text(script_content, encoding="utf-8")
        return {
            "status": "success",
            "message": "Reviewed REAL k6 script generated from workload profile.",
            "tool": tool,
            "application": application,
            "scenario": scenario,
            "api_name": api_name,
            "execution_mode": execution_mode,
            "execution_status": "prepared",
            "file_name": script_path.name,
            "file_path": str(script_path),
            "artifact_path": script_path.name,
        }

    if execution_mode != "SIMULATED":
        return {
            "status": "error",
            "message": f"Unsupported execution mode: {execution_mode}.",
            "tool": tool,
        }

    os.makedirs(
        GENERATED_SCRIPTS_DIR,
        exist_ok=True,
    )

    generator = ArtifactGenerator()

    script_content = generator.generate_script(
        tool=tool,
        application=application,
        scenario=scenario,
        api_name=api_name,
    )

    error_messages = {
        "UNSUPPORTED_TOOL": (
            f"Unsupported performance-testing tool: {tool}."
        ),
        "EMPTY_ARTIFACT": (
            "The artifact generator returned empty content."
        ),
        "INVALID_JMETER_ARTIFACT": (
            "The generated JMeter artifact failed "
            "structural validation."
        ),
        "INVALID_K6_ARTIFACT": (
            "The generated k6 artifact failed "
            "structural validation."
        ),
        "INVALID_GATLING_ARTIFACT": (
            "The generated Gatling artifact failed "
            "structural validation."
        ),
    }

    if script_content in error_messages:
        return {
            "status": "error",
            "message": error_messages[script_content],
            "tool": tool,
            "application": application,
            "scenario": scenario,
            "api_name": api_name,
        }

    if not isinstance(script_content, str):
        return {
            "status": "error",
            "message": "Generated artifact is not text content.",
            "tool": tool,
        }

    script_content = script_content.strip()

    if not script_content:
        return {
            "status": "error",
            "message": "Generated artifact is empty.",
            "tool": tool,
        }

    extension = extensions[tool]

    safe_api_name = _sanitize_filename(api_name)

    if not safe_api_name:
        safe_api_name = "performance_test"

    file_name = (
        f"{tool}_{safe_api_name}{extension}"
    )

    file_path = os.path.join(
        GENERATED_SCRIPTS_DIR,
        file_name,
    )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as script_file:

        script_file.write(script_content)

    return {
        "status": "success",
        "message": (
            "Performance-testing script generated successfully."
        ),
        "tool": tool,
        "application": application,
        "scenario": scenario,
        "api_name": api_name,
        "file_name": file_name,
        "file_path": file_path,
    }


def _sanitize_filename(api_name):

    if not api_name:
        return ""

    safe_name = api_name.strip()

    safe_name = (
        safe_name
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .replace(":", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace("=", "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace('"', "_")
        .replace("'", "_")
        .replace("|", "_")
    )

    safe_name = "".join(
        character
        for character in safe_name
        if character.isalnum()
        or character in {"_", "."}
    )

    safe_name = re.sub(r"_+", "_", safe_name)
    safe_name = safe_name.strip("._")

    return safe_name