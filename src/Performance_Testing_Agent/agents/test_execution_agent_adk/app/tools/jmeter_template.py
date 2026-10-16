"""Build and validate deterministic, profile-bound JMeter JMX plans."""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlsplit

from pydantic import ValidationError

from Performance_Testing_Agent.execution_context import (
    WorkloadProfile,
    missing_profile_inputs,
    validate_real_profile,
)

_JMETER_MAX_RPS_ENV = "REAL_JMETER_MAX_RPS"
_DEFAULT_JMETER_MAX_RPS = 1000
_BODY_METHODS = {"POST", "PUT", "PATCH"}
_THROUGHPUT_CALC_MODE_GROUP_SHARED = "4"


def _validate_profile(profile_data: dict[str, Any]) -> WorkloadProfile:
    try:
        profile = WorkloadProfile.model_validate(profile_data)
    except ValidationError as exc:
        raise ValueError(f"Invalid JMeter workload profile: {exc}") from exc

    if profile.tool != "jmeter":
        raise ValueError("The real JMeter template requires tool='jmeter'.")

    missing = missing_profile_inputs(profile)
    if missing:
        raise ValueError(
            "The real JMeter workload profile is missing: "
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
            "Real JMeter plan generation failed safety preflight: "
            + "; ".join(reasons)
        )

    if profile.endpoint is None:
        raise ValueError("The JMeter workload profile requires an endpoint.")
    if "${" in profile.endpoint or "}" in profile.endpoint:
        raise ValueError(
            "The endpoint cannot contain JMeter variable or function syntax."
        )
    for header_name, property_name in (profile.header_env or {}).items():
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", header_name):
            raise ValueError("A configured HTTP header name is invalid.")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", property_name):
            raise ValueError(
                "Header references must use simple environment/property names."
            )
    _reject_jmeter_expressions(profile.payload_template)
    return profile


def _reject_jmeter_expressions(value: Any) -> None:
    if isinstance(value, str):
        if "${" in value:
            raise ValueError(
                "Payload values cannot contain JMeter variable or function syntax."
            )
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_jmeter_expressions(key)
            _reject_jmeter_expressions(item)
    elif isinstance(value, list):
        for item in value:
            _reject_jmeter_expressions(item)


def _configured_jmeter_max_rps() -> int:
    raw_value = os.getenv(_JMETER_MAX_RPS_ENV)
    if raw_value is None:
        return _DEFAULT_JMETER_MAX_RPS
    try:
        maximum = int(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"{_JMETER_MAX_RPS_ENV} must be a positive integer."
        ) from exc
    if maximum < 1:
        raise ValueError(f"{_JMETER_MAX_RPS_ENV} must be a positive integer.")
    return maximum


def _jmeter_name(test_case_id: str | None) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_case_id or "")
    normalized = normalized.strip("_.-")
    return f"REAL JMeter {normalized}" if normalized else "REAL JMeter API Test"


def _component(
    parent: ET.Element,
    tag: str,
    gui_class: str,
    name: str,
    *,
    attributes: dict[str, str] | None = None,
) -> ET.Element:
    values = {
        "guiclass": gui_class,
        "testclass": tag,
        "testname": name,
        "enabled": "true",
    }
    if attributes:
        values.update(attributes)
    return ET.SubElement(parent, tag, values)


def _string_prop(parent: ET.Element, name: str, value: str) -> ET.Element:
    element = ET.SubElement(parent, "stringProp", {"name": name})
    element.text = value
    return element


def _bool_prop(parent: ET.Element, name: str, value: bool) -> ET.Element:
    element = ET.SubElement(parent, "boolProp", {"name": name})
    element.text = "true" if value else "false"
    return element


def _int_prop(parent: ET.Element, name: str, value: int | str) -> ET.Element:
    element = ET.SubElement(parent, "intProp", {"name": name})
    element.text = str(value)
    return element


def _long_prop(parent: ET.Element, name: str, value: int) -> ET.Element:
    element = ET.SubElement(parent, "longProp", {"name": name})
    element.text = str(value)
    return element


def _hash_tree(parent: ET.Element) -> ET.Element:
    return ET.SubElement(parent, "hashTree")


def _payload_json(profile: WorkloadProfile) -> str | None:
    if profile.method not in _BODY_METHODS or profile.payload_template is None:
        return None
    try:
        return json.dumps(
            profile.payload_template,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "The JMeter payload cannot be represented as valid JSON."
        ) from exc


def _effective_port(target) -> int:
    """Return the explicit port or the URL scheme's standard port."""
    if target.port is not None:
        return target.port
    return 443 if target.scheme == "https" else 80


def _expected_headers(profile: WorkloadProfile) -> list[tuple[str, str]]:
    headers = dict(profile.header_env or {})
    if (
        profile.method in _BODY_METHODS
        and profile.payload_template is not None
        and not any(name.lower() == "content-type" for name in headers)
    ):
        headers["Content-Type"] = ""

    return [
        (
            header_name,
            f"${{__P({environment_name},)}}" if environment_name else "application/json",
        )
        for header_name, environment_name in sorted(
            headers.items(),
            key=lambda pair: (pair[0].lower(), pair[0]),
        )
    ]


def _build_jmx(profile: WorkloadProfile, test_case_id: str | None) -> str:
    assert profile.target_url is not None
    assert profile.endpoint is not None
    assert profile.method is not None
    assert profile.users is not None
    assert profile.ramp_up_seconds is not None
    assert profile.duration_seconds is not None
    assert profile.max_rps is not None

    target = urlsplit(profile.target_url)
    test_name = _jmeter_name(test_case_id)
    root = ET.Element(
        "jmeterTestPlan",
        {"version": "1.2", "properties": "5.0", "jmeter": "5.6.3"},
    )
    plan_tree = _hash_tree(root)
    _component(plan_tree, "TestPlan", "TestPlanGui", test_name)
    plan_children = _hash_tree(plan_tree)
    _string_prop(
        plan_tree[0],
        "TestPlan.comments",
        "Generated from a validated REAL workload profile.",
    )
    _bool_prop(plan_tree[0], "TestPlan.functional_mode", False)
    _bool_prop(plan_tree[0], "TestPlan.tearDown_on_shutdown", True)
    _bool_prop(plan_tree[0], "TestPlan.serialize_threadgroups", False)
    variables = ET.SubElement(
        plan_tree[0],
        "elementProp",
        {
            "name": "TestPlan.user_defined_variables",
            "elementType": "Arguments",
            "guiclass": "ArgumentsPanel",
            "testclass": "Arguments",
            "testname": "User Defined Variables",
            "enabled": "true",
        },
    )
    ET.SubElement(variables, "collectionProp", {"name": "Arguments.arguments"})
    _string_prop(plan_tree[0], "TestPlan.user_define_classpath", "")

    thread_group = _component(
        plan_children,
        "ThreadGroup",
        "ThreadGroupGui",
        "Virtual Users",
    )
    _string_prop(thread_group, "ThreadGroup.on_sample_error", "continue")
    loop_controller = ET.SubElement(
        thread_group,
        "elementProp",
        {
            "name": "ThreadGroup.main_controller",
            "elementType": "LoopController",
            "guiclass": "LoopControlPanel",
            "testclass": "LoopController",
            "testname": "Loop Controller",
            "enabled": "true",
        },
    )
    _bool_prop(loop_controller, "LoopController.continue_forever", True)
    _string_prop(loop_controller, "LoopController.loops", "-1")
    _string_prop(thread_group, "ThreadGroup.num_threads", str(profile.users))
    _string_prop(
        thread_group,
        "ThreadGroup.ramp_time",
        str(profile.ramp_up_seconds),
    )
    _long_prop(thread_group, "ThreadGroup.start_time", 0)
    _long_prop(thread_group, "ThreadGroup.end_time", 0)
    _bool_prop(thread_group, "ThreadGroup.scheduler", True)
    _string_prop(
        thread_group,
        "ThreadGroup.duration",
        str(profile.duration_seconds),
    )
    _string_prop(thread_group, "ThreadGroup.delay", "0")
    _bool_prop(thread_group, "ThreadGroup.same_user_on_next_iteration", True)

    thread_tree = _hash_tree(plan_children)
    timer = _component(
        thread_tree,
        "ConstantThroughputTimer",
        "ThroughputTimerGui",
        "Maximum Request Rate",
    )
    _string_prop(
        timer,
        "ConstantThroughputTimer.throughput",
        str(profile.max_rps * 60),
    )
    _int_prop(timer, "calcMode", _THROUGHPUT_CALC_MODE_GROUP_SHARED)
    _hash_tree(thread_tree)

    sampler = _component(
        thread_tree,
        "HTTPSamplerProxy",
        "HttpTestSampleGui",
        "API Request",
    )
    arguments = ET.SubElement(
        sampler,
        "elementProp",
        {
            "name": "HTTPsampler.Arguments",
            "elementType": "Arguments",
            "guiclass": "HTTPArgumentsPanel",
            "testclass": "Arguments",
            "testname": "User Defined Variables",
            "enabled": "true",
        },
    )
    argument_collection = ET.SubElement(
        arguments,
        "collectionProp",
        {"name": "Arguments.arguments"},
    )
    payload = _payload_json(profile)
    if payload is not None:
        body_argument = ET.SubElement(
            argument_collection,
            "elementProp",
            {"name": "", "elementType": "HTTPArgument"},
        )
        _bool_prop(body_argument, "HTTPArgument.always_encode", False)
        _string_prop(body_argument, "Argument.value", payload)
        _string_prop(body_argument, "Argument.metadata", "=")
        _bool_prop(body_argument, "HTTPArgument.use_equals", True)
        _string_prop(body_argument, "Argument.name", "")

    _string_prop(sampler, "HTTPSampler.domain", target.hostname or "")
    _string_prop(sampler, "HTTPSampler.port", str(_effective_port(target)))
    _string_prop(sampler, "HTTPSampler.protocol", target.scheme)
    _string_prop(sampler, "HTTPSampler.contentEncoding", "UTF-8")
    _string_prop(sampler, "HTTPSampler.path", profile.endpoint)
    _string_prop(sampler, "HTTPSampler.method", profile.method)
    _bool_prop(sampler, "HTTPSampler.follow_redirects", False)
    _bool_prop(sampler, "HTTPSampler.auto_redirects", False)
    _bool_prop(sampler, "HTTPSampler.use_keepalive", True)
    _bool_prop(sampler, "HTTPSampler.DO_MULTIPART_POST", False)
    _string_prop(sampler, "HTTPSampler.embedded_url_re", "")
    _string_prop(sampler, "HTTPSampler.connect_timeout", "")
    _string_prop(sampler, "HTTPSampler.response_timeout", "")
    _bool_prop(sampler, "HTTPSampler.postBodyRaw", payload is not None)
    _string_prop(sampler, "HTTPSampler.implementation", "HttpClient4")

    sampler_tree = _hash_tree(thread_tree)
    headers = _component(
        sampler_tree,
        "HeaderManager",
        "HeaderPanel",
        "HTTP Headers",
    )
    header_collection = ET.SubElement(
        headers,
        "collectionProp",
        {"name": "HeaderManager.headers"},
    )
    for header_name, header_value in _expected_headers(profile):
        header = ET.SubElement(
            header_collection,
            "elementProp",
            {"name": header_name, "elementType": "Header"},
        )
        _string_prop(header, "Header.name", header_name)
        _string_prop(header, "Header.value", header_value)
    _hash_tree(sampler_tree)

    ET.indent(root, space="  ")
    return (
        ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        + "\n"
    )


def validate_real_jmeter_plan(
    jmx_content: str,
    workload_profile: dict[str, Any],
    test_case_id: str | None = None,
) -> None:
    """Reject malformed plans and plans that differ from the trusted profile."""
    profile = _validate_profile(workload_profile)
    assert profile.target_url is not None
    assert profile.endpoint is not None
    assert profile.method is not None
    assert profile.users is not None
    assert profile.ramp_up_seconds is not None
    assert profile.duration_seconds is not None
    assert profile.max_rps is not None

    maximum_rps = _configured_jmeter_max_rps()
    if profile.max_rps > maximum_rps:
        raise ValueError(
            f"max_rps exceeds the configured JMeter ceiling of {maximum_rps}."
        )

    try:
        if "<!DOCTYPE" in jmx_content.upper() or "<!ENTITY" in jmx_content.upper():
            raise ValueError("The JMeter plan cannot contain a DTD or entity declaration.")
        root = ET.fromstring(jmx_content)
    except (ET.ParseError, TypeError) as exc:
        raise ValueError("The generated JMeter plan is not valid XML.") from exc
    if root.tag != "jmeterTestPlan":
        raise ValueError("The generated JMeter plan has an invalid root element.")

    test_plans = root.findall(".//TestPlan")
    thread_groups = root.findall(".//ThreadGroup")
    samplers = root.findall(".//HTTPSamplerProxy")
    timers = root.findall(".//ConstantThroughputTimer")
    if not (
        len(test_plans) == len(thread_groups) == len(samplers) == len(timers) == 1
    ):
        raise ValueError(
            "The JMeter plan must contain one plan, group, sampler, and rate timer."
        )
    if any(
        root.findall(f".//{tag}")
        for tag in (
            "BeanShellSampler",
            "BeanShellPreProcessor",
            "BeanShellPostProcessor",
            "JSR223Sampler",
            "JSR223PreProcessor",
            "JSR223PostProcessor",
            "OSProcessSampler",
        )
    ):
        raise ValueError("The JMeter plan contains a disallowed executable component.")

    target = urlsplit(profile.target_url)
    sampler = samplers[0]
    expected_sampler_values = {
        "HTTPSampler.domain": target.hostname or "",
        "HTTPSampler.port": str(_effective_port(target)),
        "HTTPSampler.protocol": target.scheme,
        "HTTPSampler.path": profile.endpoint,
        "HTTPSampler.method": profile.method,
    }
    for prop_name, expected in expected_sampler_values.items():
        actual = sampler.find(f"stringProp[@name='{prop_name}']")
        if actual is None or actual.text != expected:
            raise ValueError(
                f"JMeter sampler setting {prop_name} does not match the trusted profile."
            )

    thread_group = thread_groups[0]
    expected_group_values = {
        "ThreadGroup.num_threads": str(profile.users),
        "ThreadGroup.ramp_time": str(profile.ramp_up_seconds),
        "ThreadGroup.duration": str(profile.duration_seconds),
    }
    for prop_name, expected in expected_group_values.items():
        actual = thread_group.find(f"stringProp[@name='{prop_name}']")
        if actual is None or actual.text != expected:
            raise ValueError(
                f"JMeter workload setting {prop_name} does not match the trusted profile."
            )
    scheduler = thread_group.find("boolProp[@name='ThreadGroup.scheduler']")
    if scheduler is None or scheduler.text != "true":
        raise ValueError("JMeter thread scheduling must use the profile duration.")

    timer = timers[0]
    throughput = timer.find(
        "stringProp[@name='ConstantThroughputTimer.throughput']"
    )
    calc_mode = timer.find("intProp[@name='calcMode']")
    if (
        throughput is None
        or throughput.text != str(profile.max_rps * 60)
        or calc_mode is None
        or calc_mode.text != _THROUGHPUT_CALC_MODE_GROUP_SHARED
    ):
        raise ValueError(
            "JMeter throughput settings do not match the profile's max_rps ceiling."
        )

    argument_value = sampler.find(
        ".//elementProp[@elementType='HTTPArgument']/stringProp[@name='Argument.value']"
    )
    expected_payload = _payload_json(profile)
    if (argument_value.text if argument_value is not None else None) != expected_payload:
        raise ValueError("JMeter request payload does not match the trusted profile.")

    header_manager = root.find(".//HeaderManager")
    actual_headers: list[tuple[str, str]] = []
    if header_manager is not None:
        for header in header_manager.findall(
            "collectionProp[@name='HeaderManager.headers']/elementProp"
        ):
            name = header.find("stringProp[@name='Header.name']")
            value = header.find("stringProp[@name='Header.value']")
            actual_headers.append(
                (
                    name.text if name is not None and name.text else "",
                    value.text if value is not None and value.text else "",
                )
            )
    if actual_headers != _expected_headers(profile):
        raise ValueError("JMeter request headers do not match the trusted profile.")

    expected_name = _jmeter_name(test_case_id)
    if test_plans[0].get("testname") != expected_name:
        raise ValueError("The JMeter test-plan name does not match this test case.")

    expected_content = ET.fromstring(_build_jmx(profile, test_case_id))
    if ET.tostring(root, encoding="utf-8") != ET.tostring(
        expected_content,
        encoding="utf-8",
    ):
        raise ValueError(
            "The JMeter plan contains structure or settings outside the "
            "reviewed deterministic template."
        )


def build_real_jmeter_plan(
    workload_profile: dict[str, Any],
    test_case_id: str | None = None,
) -> str:
    """Build a deterministic JMX document and verify all profile-bound fields."""
    profile = _validate_profile(workload_profile)
    assert profile.max_rps is not None
    maximum_rps = _configured_jmeter_max_rps()
    if profile.max_rps > maximum_rps:
        raise ValueError(
            f"max_rps exceeds the configured JMeter ceiling of {maximum_rps}."
        )
    content = _build_jmx(profile, test_case_id)
    validate_real_jmeter_plan(
        content,
        profile.model_dump(mode="json"),
        test_case_id,
    )
    return content


__all__ = ["build_real_jmeter_plan", "validate_real_jmeter_plan"]
