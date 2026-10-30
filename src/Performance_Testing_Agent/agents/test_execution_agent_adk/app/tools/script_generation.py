import os
import re
import tempfile
from pathlib import Path

from app.tools.artifact_generator import ArtifactGenerator
from app.tools.jmeter_template import (
    build_real_jmeter_plan,
    validate_real_jmeter_plan,
)
from app.tools.k6_template import build_real_k6_script
from app.tools.script_library import reuse_or_build
from Performance_Testing_Agent.execution_context import (
    WorkloadProfile,
    artifact_root_directory,
    missing_profile_inputs,
    resolve_artifact_directory,
    validate_real_profile,
    workload_profile_from_test_case,
)


GENERATED_SCRIPTS_DIR = str(
    Path(__file__).resolve().parents[5] / "generated_scripts"
)


def _reuse_message(kind: str, test_case_id) -> str:
    """Say plainly that nothing was regenerated, so a reused script is not mistaken for a new one."""
    subject = f"for {test_case_id} " if test_case_id else ""
    return (
        f"Reviewed REAL {kind} {subject}reused from the stored script (the workload is "
        "unchanged, so it was not regenerated) and copied into the job artifact directory."
    )


def _verify_reused_k6_script(profile_data: dict) -> None:
    """Re-run the checks build_real_k6_script applies before it renders.

    A stored k6 script is only reused if the profile still passes the same
    validation and safety preflight (host allowlist, limits) as a fresh build.
    Raises ValueError otherwise, and the caller then builds normally.
    """
    profile = WorkloadProfile.model_validate(profile_data)
    if profile.tool != "k6":
        raise ValueError("The real k6 template requires tool='k6'.")
    missing = missing_profile_inputs(profile)
    if missing:
        raise ValueError("The real k6 workload profile is missing: " + ", ".join(missing))
    preflight = validate_real_profile(profile)
    if preflight["status"] != "ready":
        raise ValueError("Real k6 script generation failed safety preflight.")


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
        if tool == "jmeter":
            if not isinstance(workload_profile, dict):
                return {
                    "status": "error",
                    "message": (
                        "REAL JMeter script generation requires the trusted "
                        "workload profile from session state."
                    ),
                    "tool": tool,
                    "execution_mode": execution_mode,
                }
            if not job_id:
                return {
                    "status": "error",
                    "message": "REAL JMeter script generation requires a job_id.",
                    "tool": tool,
                    "execution_mode": execution_mode,
                }
            if artifact_directory is None:
                return {
                    "status": "error",
                    "message": (
                        "REAL JMeter script generation requires the job "
                        "artifact directory."
                    ),
                    "tool": tool,
                    "execution_mode": execution_mode,
                }

            try:
                profile = workload_profile_from_test_case(
                    {"workload_profile": workload_profile}
                )
                artifact_root = artifact_root_directory("jmeter")
                expected_directory = resolve_artifact_directory(
                    job_id,
                    tool="jmeter",
                )
                candidate_directory = artifact_root / job_id
                if candidate_directory.is_symlink():
                    raise ValueError(
                        "The JMeter job artifact directory cannot be a symbolic link."
                    )
                if expected_directory.parent != artifact_root:
                    raise ValueError(
                        "The JMeter job artifact directory is outside the artifact root."
                    )
                supplied_directory = Path(artifact_directory).expanduser().resolve()
                if supplied_directory != expected_directory:
                    raise ValueError(
                        "The supplied artifact directory does not match this job."
                    )

                profile_data = profile.model_dump(mode="json")
                script_content, script_source = reuse_or_build(
                    "jmeter",
                    profile_data,
                    test_case_id,
                    build=lambda: build_real_jmeter_plan(
                        profile_data,
                        test_case_id=test_case_id,
                    ),
                    verify=lambda content: validate_real_jmeter_plan(
                        content,
                        profile_data,
                        test_case_id,
                    ),
                )
                safe_test_case_id = _sanitize_filename(test_case_id or "")[:64]
                filename_part = safe_test_case_id or "api_test"
                file_name = f"jmeter_{filename_part}_plan.jmx"
                job_directory = expected_directory
                job_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
                if job_directory.is_symlink() or job_directory.resolve() != job_directory:
                    raise ValueError(
                        "The JMeter job artifact directory changed during generation."
                    )

                script_path = job_directory / file_name
                file_descriptor, temporary_name = tempfile.mkstemp(
                    prefix=f".{file_name}.",
                    suffix=".tmp",
                    dir=job_directory,
                )
                try:
                    with os.fdopen(
                        file_descriptor,
                        "w",
                        encoding="utf-8",
                        newline="\n",
                    ) as script_file:
                        os.fchmod(script_file.fileno(), 0o644)
                        script_file.write(script_content)
                        script_file.flush()
                        os.fsync(script_file.fileno())
                    os.replace(temporary_name, script_path)
                finally:
                    Path(temporary_name).unlink(missing_ok=True)
            except (OSError, RuntimeError, ValueError) as exc:
                return {
                    "status": "error",
                    "message": str(exc),
                    "tool": tool,
                    "execution_mode": execution_mode,
                }

            return {
                "status": "success",
                "message": (
                    _reuse_message("JMeter plan", test_case_id)
                    if script_source == "reused"
                    else (
                        "Reviewed REAL JMeter plan generated from the trusted "
                        "workload profile and saved in the job artifact directory."
                    )
                ),
                "tool": tool,
                "application": application,
                "scenario": scenario,
                "api_name": api_name,
                "execution_mode": execution_mode,
                "execution_status": "prepared",
                "file_name": file_name,
                "file_path": str(script_path),
                "artifact_path": file_name,
                "script_source": script_source,
            }

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
            expected_directory = resolve_artifact_directory(job_id, tool="k6")
            if artifact_directory is None:
                raise ValueError("REAL k6 generation requires a job artifact directory.")
            job_directory = Path(artifact_directory).expanduser().resolve()
            if job_directory != expected_directory:
                raise ValueError(
                    "The supplied artifact directory does not match this job."
                )
            profile_data = profile.model_dump(mode="json")
            script_content, script_source = reuse_or_build(
                "k6",
                profile_data,
                test_case_id,
                build=lambda: build_real_k6_script(
                    profile_data,
                    test_case_id=test_case_id,
                ),
                verify=lambda content: _verify_reused_k6_script(profile_data),
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
            "message": (
                _reuse_message("k6 script", test_case_id)
                if script_source == "reused"
                else "Reviewed REAL k6 script generated from workload profile."
            ),
            "tool": tool,
            "application": application,
            "scenario": scenario,
            "api_name": api_name,
            "execution_mode": execution_mode,
            "execution_status": "prepared",
            "file_name": script_path.name,
            "file_path": str(script_path),
            "artifact_path": script_path.name,
            "script_source": script_source,
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
