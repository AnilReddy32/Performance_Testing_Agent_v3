import json
from typing import Any

from pydantic import ValidationError

from Performance_Testing_Agent.execution_context import (
    WorkloadProfile,
    missing_profile_inputs,
    validate_real_profile,
)


def build_real_k6_script(
    workload_profile: dict[str, Any],
    test_case_id: str | None = None,
) -> str:
    """Build a reviewed, deterministic k6 script from trusted profile data."""
    try:
        profile = WorkloadProfile.model_validate(workload_profile)
    except ValidationError as exc:
        raise ValueError(f"Invalid k6 workload profile: {exc}") from exc

    if profile.tool != "k6":
        raise ValueError("The real k6 template requires tool='k6'.")

    missing = missing_profile_inputs(profile)
    if missing:
        raise ValueError(
            "The real k6 workload profile is missing: "
            + ", ".join(missing)
            + "."
        )

    preflight = validate_real_profile(profile)
    if preflight["status"] != "ready":
        reasons = preflight.get("blocked_reasons", [])
        if preflight.get("missing_inputs"):
            reasons = [
                "Missing inputs: " + ", ".join(preflight["missing_inputs"])
            ]
        raise ValueError(
            "Real k6 script generation failed safety preflight: "
            + "; ".join(reasons)
        )

    assert profile.endpoint is not None
    assert profile.method is not None
    assert profile.users is not None
    assert profile.max_rps is not None
    assert profile.duration_seconds is not None
    assert profile.ramp_up_seconds is not None
    assert profile.expected_status_code is not None
    assert profile.p95_threshold_ms is not None

    hold_seconds = profile.duration_seconds - (2 * profile.ramp_up_seconds)
    stages = [
        {"duration": f"{profile.ramp_up_seconds}s", "target": profile.users}
    ]
    if hold_seconds:
        stages.append({"duration": f"{hold_seconds}s", "target": profile.users})
    stages.append(
        {"duration": f"{profile.ramp_up_seconds}s", "target": 0}
    )

    try:
        stages_json = json.dumps(stages, separators=(",", ":"), allow_nan=False)
        tags_json = json.dumps(
            {
                "test_case_id": test_case_id or "unspecified",
                "endpoint": profile.endpoint,
                "environment": profile.environment,
            },
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        payload_json = (
            json.dumps(
                profile.payload_template,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            if profile.payload_template is not None
            else "null"
        )
        endpoint_json = json.dumps(
            profile.endpoint,
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "The k6 workload profile contains values that cannot be "
            "represented as valid JSON."
        ) from exc

    has_json_body = profile.method in {"POST", "PUT", "PATCH"}
    body_template_js = json.dumps(payload_json) if has_json_body else "null"
    content_type_header = (
        "    'Content-Type': 'application/json',\n"
        if has_json_body
        else ""
    )
    case_id_json = json.dumps(
        test_case_id or "unspecified",
        ensure_ascii=True,
    )

    return f"""import http from 'k6/http';
import {{ check }} from 'k6';

const BASE_URL = __ENV.BASE_URL;
const ENDPOINT = {endpoint_json};
const METHOD = {json.dumps(profile.method)};
const BODY_TEMPLATE = {body_template_js};
const EXPECTED_STATUS = {profile.expected_status_code};

if (!BASE_URL) {{
  throw new Error('BASE_URL must be provided by the trusted execution runner.');
}}

export const options = {{
  stages: {stages_json},
  rps: {profile.max_rps},
  thresholds: {{
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<{profile.p95_threshold_ms}'],
    checks: ['rate>0.99'],
  }},
  tags: {tags_json},
}};

export default function () {{
  const headers = {{
{content_type_header}  }};
  if (__ENV.AUTHORIZATION_HEADER) {{
    headers.Authorization = __ENV.AUTHORIZATION_HEADER;
  }}
  const requestBody = BODY_TEMPLATE === null
    ? null
    : BODY_TEMPLATE
        .replace(/\\{{\\{{__VU\\}}\\}}/g, String(__VU))
        .replace(/\\{{\\{{__ITER\\}}\\}}/g, String(__ITER));

  const response = http.request(
    METHOD,
    `${{BASE_URL.replace(/\\/+$/, '')}}${{ENDPOINT}}`,
    requestBody,
    {{
      headers,
      redirects: 0,
      tags: {{
        test_case_id: {case_id_json},
        endpoint: ENDPOINT,
      }},
    }},
  );

  check(response, {{
    [`expected HTTP ${{EXPECTED_STATUS}}`]: (res) => res.status === EXPECTED_STATUS,
  }});
}}
"""


__all__ = ["build_real_k6_script"]
