import os

from app.tools.artifact_generator import ArtifactGenerator


GENERATED_SCRIPTS_DIR = "generated_scripts"
# from pathlib import Path
# GENERATED_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent / "generated_scripts")



def generate_script(
    tool,
    application,
    scenario,
    api_name,
):

    os.makedirs(
        GENERATED_SCRIPTS_DIR,
        exist_ok=True,
    )

    tool = tool.lower().strip()

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

    safe_name = safe_name.strip("._")

    return safe_name